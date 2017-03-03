#-*- coding: utf-8 -*-
import re

def set_pass(chat_id, text):
    sites = re.split(r'[\s]',text)

    sql_select = "select * from pass_check where address=%s"

    sql_insert = ""
