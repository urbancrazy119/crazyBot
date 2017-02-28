#-*- coding: utf-8 -*-
import urllib
import urllib2
import json
import logging
import re
import requests
import time

#import pymysql
import database as db

import sys
import info
import mappingList as m
import funcWeather as weather
import funcBowl as bowl

# important information
TOKEN = info.TOKEN
BASE_URL = 'https://api.telegram.org/bot'+TOKEN+'/'

# command
CMD_START   = '/start'
CMD_STOP    = '/stop'
CMD_HELP    = '/help'
CMD_WEATHER = '날씨'
CMD_BOWL_IN = '볼링'
CMD_BOWL_OU = '점수'

# usage for help
USAGE = u"""[사용법]
/start      - 알림 시작
/stop       - 알림 종료
/help       - 도움말
날씨        - 오늘의 날씨
볼링 점수   - 볼링점수 입력
점수        - 볼링점수 확인(최근 3일 및 총 에버)

알림 : 매일 아침 5:30 날씨를 알려드립니다.
"""
MSG_START   = u'봇 시작'
MSG_STOP    = u'봇 종료'

# custom keyboard
CUSTOM_KEYBOARD = [
        [CMD_START],
        [CMD_STOP],
        [CMD_HELP],
    ]

def set_enabled(chat_id, enabled):
    u"""set_enabled: bot status update
    chat_id:    (integer)   chat ID
    enbaled:    (boolean)   status (0 = disabled, 1 = enabled)
    """
    (cur,conn)=db.conn_db()
    try:
        sql_select = "select count(*) from user_status where chat_id=%s"
        cur.execute(sql_select, (chat_id,))
        count = cur.fetchone()[0]
        # if 
        if count == 1:
            sql_update = "update user_status set chat_status=%s where chat_id=%s"
            cur.execute(sql_update, (enabled, chat_id,))
        # if new cusomer
        elif count == 0:
            sql_insert = "insert into user_status(chat_id, chat_status) values (%s, %s)"
            cur.execute(sql_insert, (chat_id, enabled,))

    finally:
        db.disconn_db(conn)

def get_enabled(chat_id):
    u"""get_enabled: return status of chat_id
    chat_id:    (integer)   chat ID

    return :    (boolean)   status
    """
    (cur, conn) = db.conn_db()
    sql_select  = "select chat_status from user_status where chat_id=%s"
    cur.execute(sql_select, (chat_id,))
    res = cur.fetchone()

    db.disconn_db(conn)
    return res

def get_enabled_user():
    u"""get_enabled_user
    return :    (list)      Chat ID list
    """
    (cur,conn) = db.conn_db()
    sql_select = "select chat_id from user_status where chat_status=1"
    cur.execute(sql_select)
    rows = cur.fetchall()
    return rows

def get_module_user(module):
    (cur,conn) = db.conn_db()
    sql_select = "select chat_id from user_status where %s_status=1"%module
    cur.execute(sql_select)
    rows = cur.fetchall()
    return rows

def get_url(url):
    u"""get_url:    get content from url
    url:    (string)    URL
    """
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    u"""get_json_from_url:  get json code from url
    url:    (string)    URL
    """
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates():
    u"""get_updates: get from bot chat data
    """
    url = BASE_URL+"getUpdates"
    js = get_json_from_url(url)
    return js

def set_last_chat_id_and_text(updates):
    u"""set_last_chat_id_and_text: get last msg from url and insert database
    updates:    ()  
    """
    (cur,conn) = db.conn_db()
    sql_select = "select max(update_id) as max_num from cmd_history where run_chk ='N'"
    cur.execute(sql_select)
    max_update_id = cur.fetchone()[0]
    if not max_update_id :
        sql_select = "select max(update_id) as max_num from cmd_history where run_chk ='Y'"
        cur.execute(sql_select)
        max_update_id = cur.fetchone()[0]+1
    try:
        num_updates = len(updates["result"])
        loop_end = num_updates-1
        last_update_id = updates["result"][loop_end]["update_id"]
        loop_start = loop_end-(last_update_id-max_update_id)

        print loop_start, loop_end
        print updates["result"][loop_end]

        while loop_start<num_updates:
            chat_id     = updates["result"][loop_start]["message"]["chat"]["id"]
            update_id   = updates["result"][loop_start]["update_id"]
            msg_id      = updates["result"][loop_start]["message"]["message_id"]
            msg_text    = updates["result"][loop_start]["message"]["text"]

            loop_start += 1
            try :
                sql_insert = "insert into cmd_history(update_id, chat_id, msg_id, msg_text ) values (%s, %s, %s, %s)"
                cur.execute(sql_insert, (update_id, chat_id, msg_id, msg_text))
            except :
                time.sleep(0.5)
                #print "Unexpected error:", sys.exc_info()[0]
            time.sleep(0.5)
       
    finally:
        db.disconn_db(conn)

def get_cmd_history():
    u"""get_cmd_history:    get cmd list that run_chk = 'N'
    """
    (cur,conn) = db.conn_db()
    sql_select = "select chat_id, msg_text, update_id from cmd_history where run_chk = 'N'"
    cur.execute(sql_select)
    rows = cur.fetchall()

    for i in rows:

        process_cmds(i[0],i[1])
        try:
            sql_update = "update cmd_history set run_chk ='Y' where update_id = %s"
            cur.execute(sql_update,(i[2],))
        finally:
            conn.commit()


def send_msg(chat_id, text, reply_to=None, no_preview=False, keyboard=None):
    u"""
    chat_id:    (integer)   Chat ID
    text:       (string)    Message
    reply_to:   (integer)   reply to ~ message
    no_preview: (boolean)   URL preview on/off
    kyboard:    (list)      custom keyboard
    """
    if chat_id == 319019079:
        text+='\n현정아 사랑해'
    params ={
            'chat_id':str(chat_id),
            'text':text.encode('utf-8')
            }
    if reply_to:
        params['reply_to_message_id'] = reply_to
    if no_preview:
        params['disable_web_page_preview'] = no_preview
    if keyboard:
        reply_markup =json.dump({
            'keyboard':keyboard,
            'resize_keyboard':True,
            'one_time_keyboard':False,
            'selective':(reply_to != None),
            })
        prarmas['reply_markup'] = reply_markup
    try:
        urllib2.urlopen(BASE_URL+'sendMessage', urllib.urlencode(params)).read()
    except Exception as e:
        logging.exception(e)

def broadcast(text):
    u"""broadcast:  send to all user who enabled chat status
    text:       (string)    Message
    """
    for chat in get_enabled_user():
        send_msg(chat[0],text)
        time.sleep(0.5)

def broadcast_option(module,text):
    for chat in get_module_user(module):
        send_msg(chat[0],text)
        time.sleep(0.5)

def cmd_start(chat_id):
    u"""cmd_start: chat start
    chat_id:    (integer)   Chat ID
    """
    set_enabled(chat_id,True)
    send_msg(chat_id,'BroadCast Start')

def cmd_stop(chat_id):
    u"""cmd_stop: chat stop
    chat_id:    (integer)   Chat ID
    """
    set_enabled(chat_id,False)
    send_msg(chat_id,'BroadCast Stop')

def cmd_help(chat_id):
    u"""cmd_help: bot Help Menu
    chat_id:    (integer)   Chat ID
    """
    send_msg(chat_id, USAGE)

def cmd_weather(chat_id, city='Seoul'):
    u"""cmd_weather: weather cast
    chat_id :   (integer)   Chat ID
    city    :   (String)    City Name
    """
    msg = weather.make_weather_msg()
    send_msg(chat_id,msg)

def cmd_bowl_input(chat_id, text):
    u"""cmd_bowl_input: insert bowl score using chat_id
    chat_id :   (integer)   Chat ID
    text    :   (String)    Score
    """
    msg = bowl.set_score(chat_id, text)
    msg = '금일의 에버는 %d'%(msg)
    send_msg(chat_id,msg)

def cmd_bowl_output(chat_id):
    u"""cmd_bowl_ouput: show list chat_id's score
    chat_id :   (integer)   Chat ID
    """
    msg = bowl.get_score(chat_id)
    send_msg(chat_id,msg)

def process_cmds(chat_id, text):
    u"""process_cmds: switch CMD
    chat_id:    (integer)
    text:       (string)
    """
    if(not text):
        return
    cmd_list = re.split(r'[\s]',text)
    print cmd_list
    if CMD_START    == cmd_list[0]:
        cmd_start(chat_id)
    elif CMD_STOP     == cmd_list[0]:
        cmd_stop(chat_id)
    elif CMD_HELP     == cmd_list[0]:
        cmd_help(chat_id)
    elif CMD_WEATHER  == cmd_list[0]:
        cmd_weather(chat_id)
    elif CMD_BOWL_IN  == cmd_list[0]:
        cmd_list.pop(0)
        cmd_bowl_input(chat_id, cmd_list)
    elif CMD_BOWL_OU  == cmd_list[0]:
        cmd_bowl_output(chat_id)
    else:
        cmd_help(chat_id)

    return

def main():
    while True:
        get_cmd_history()       
        time.sleep(0.5)


