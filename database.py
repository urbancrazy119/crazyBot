#-*- coding: utf-8 -*-
import pymysql
import info

def conn_db():
    conn = pymysql.connect(host='localhost', user=info.USER, password=info.PW, db=info.DB, charset='utf8')
    cur = conn.cursor()

    return (cur,conn)

def disconn_db(conn):
    conn.commit()
    conn.close()
