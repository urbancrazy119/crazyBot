#-*- coding: utf-8 -*-
import re
from time import localtime, strftime
import database as db

def set_score(chat_id, text):
    score_list = text
    (cur,conn) = db.conn_db()
    try:
        sql_insert = "insert into bowl_score(chat_id, bowl_seq, bowl_score) values (%s, %s, %s)"
        for i in score_list:
            # numbering check
            try:
                score = int(i)
                if score<0:
                    continue
            except UnicodeEncodeError:
                continue
            except ValueError:
                continue
            except:
                continue
            # select max value
            sql_select = "select ifnull(max(bowl_seq),0) from bowl_score where date(bowl_date) = date_format(now(),'%Y-%m-%d') and chat_id = "+"%d"%(chat_id)
            cur.execute(sql_select)
            max_seq = cur.fetchone()[0]
            # insert
            
            cur.execute(sql_insert,(chat_id, max_seq+1, i))
        # today average
        sql_avg = "select ifnull(avg(bowl_score),0) from bowl_score where date(bowl_date) = date_format(now(), '%Y-%m-%d') and chat_id = "+"%d"%(chat_id)
        cur.execute(sql_avg)
        avg = cur.fetchone()[0]
    finally:
        db.disconn_db(conn)
    return avg

def get_score(chat_id):
    msg = ''
    (cur, conn) = db.conn_db()
    sql_select = "select cast(date_format(bowl_date,'%Y-%m-%d') as char), bowl_seq, bowl_score from bowl_score where bowl_date >= (CURDATE() - INTERVAL 3 DAY) and chat_id = "+"%s"%(chat_id)
    
    cur.execute(sql_select)
    data = cur.fetchall()
    for i in data:
        msg+= '[%s] %s번째 : %s\n'%(i[0], i[1], i[2])

    # avg
    sql_avg = "select ifnull(avg(bowl_score),0) from bowl_score where chat_id = %s"
    cur.execute(sql_avg, (chat_id,))
    avg = cur.fetchone()[0]
    msg+= '총 에버 : %s'%avg

    return msg

