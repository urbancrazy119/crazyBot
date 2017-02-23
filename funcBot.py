#-*- coding: utf-8 -*-
import urllib
import urllib2
import json
import logging
#import re
import requests
import time

import pymysql

import funcWeather as weather
import info

# important information
TOKEN = info.TOKEN
BASE_URL = 'https://api.telegram.org/bot'+TOKEN+'/'

# command
CMD_START   = '/start'
CMD_STOP    = '/stop'
CMD_HELP    = '/help'
CMD_WEATHER = '날씨'

# usage for help
USAGE = u"""[사용법]
/start  - 봇 시작
/stop   - 봇 종료
/help   - 도움말
"""
MSG_START   = u'봇 시작'
MSG_STOP    = u'봇 종료'

# custom keyboard
CUSTOM_KEYBOARD = [
        [CMD_START],
        [CMD_STOP],
        [CMD_HELP],
    ]

def conn_db():
    u"""conn_db:    DB connect

    return :    (cur, conn)
    """
    conn = pymysql.connect(host='localhost', user=info.USER, password=info.PW, db=info.DB, charset='utf8')
    cur = conn.cursor()

    return (cur, conn)

def disconn_db(conn):
    u"""disconn_db: DB disconnect
    """
    conn.commit()
    conn.close()

def set_enabled(chat_id, enabled):
    u"""set_enabled: bot status update
    chat_id:    (integer)   chat ID
    enbaled:    (boolean)   status (0 = disabled, 1 = enabled)
    """
    (cur,conn)=conn_db()
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
        disconn_db(conn)

def get_enabled(chat_id):
    u"""get_enabled: return status of chat_id
    chat_id:    (integer)   chat ID

    return :    (boolean)   status
    """
    (cur, conn) = conn_db()
    sql_select  = "select chat_status from user_status where chat_id=%s"
    cur.execute(sql_select, (chat_id,))
    res = cur.fetchone()

    disconn_db(conn)
    return res

def get_enabled_user():
    u"""get_enabled_user
    return :    (list)      Chat ID list
    """
    (cur,conn) = conn_db()
    sql_select = "select chat_id from user_status where chat_status=1"
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

def get_last_chat_id_and_text(updates):
    u"""get_last_chat_id_and_text
    updates:    ()  

    return :    (text,chat_id)
    """
    num_updates = len(updates["result"])
    last_update = num_updates -1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]

    return (text,chat_id)

def send_msg(chat_id, text, reply_to=None, no_preview=False, keyboard=None):
    u"""
    chat_id:    (integer)   Chat ID
    text:       (string)    Message
    reply_to:   (integer)   reply to ~ message
    no_preview: (boolean)   URL preview on/off
    kyboard:    (list)      custom keyboard
    """
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

def cmd_start(chat_id):
    u"""cmd_start: chat start
    chat_id:    (integer)   Chat ID
    """
    set_enabled(chat_id,True)
    send_msg(chat_id,'Start')

def cmd_stop(chat_id):
    u"""cmd_stop: chat stop
    chat_id:    (integer)   Chat ID
    """
    set_enabled(chat_id,False)
    send_msg(chat_id,'Stop')

def cmd_weather(chat_id):
    msg = weather.make_weather_msg()
    send_msg(chat_id,msg)

def process_cmds(chat_id, text):
    u"""process_cmds: switch CMD
    chat_id:    (integer)
    text:       (string)
    """
    if(not text):
        return
    if CMD_START == text:
        cmd_start(chat_id)
    if CMD_STOP == text:
        cmd_stop(chat_id)
    if CMD_WEATHER==text:
        cmd_weather(chat_id)

    return

def main():
    last_textchat = (None, None)
    while True:
        text, chat = get_last_chat_id_and_text(get_updates())
        if (text, chat) != last_textchat:
            process_cmds(chat, text)
            last_textchat = (text,chat)
        time.sleep(0.5)


