#-*- coding: utf-8 -*-
import requests
import hashlib
import re
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

PATH = '/usr/script/teleBot/log/'

URL = 'http://cafe.naver.com/ArticleList.nhn?search.clubid=16996348&search.menuid=175&search.boardtype=L'

def get_news():
    with requests.Session() as c:
        html = c.get(URL)
        soup = BeautifulSoup(html.text)
        parse = soup.find_all("form",{"name":"ArticleList"})

        temp_cnt = parse[0].find_all("span",{"class":"list-count"})
        temp_cont= parse[0].find_all("a",{"class":"m-tcol-c"})

        file = open(PATH+'md5_job.log','a')
        file2= open(PATH+'job_temp.log','r+')
        lines = file2.readlines()
        file2.close()
        str = ''
        for node in temp_cnt:
            txt = node.find_all(text=True)
            str += txt[0]+'\n'

        m = hashlib.md5(str)
        print >> file, m.hexdigest()
        file.close()

        file = open(PATH+'md5_job.log','r')
        md5_lines = file.readlines()
        file.close()

        file2= open(PATH+'job_temp.log','w+')
        msg_cnt = ''
        msg = ''
        for index, node in enumerate(temp_cnt):
            msg_cnt+=node.find_all(text=True)[0]+'\n'
        print >> file2, msg_cnt

        for index, node in enumerate(temp_cont):
            if index%2==0:
                msg+=node.find_all(text=True)[0]+'\n'

        file2.close()
        if len(md5_lines)<2:
            return msg
        else:
            cnt = len(md5_lines)-1
            if md5_lines[cnt-1] != md5_lines[cnt]:
                lists = []
                for index, node in enumerate(temp_cnt):
                    if node.find_all(text=True)[0]+'\n' in lines:
                        continue
                    else:
                        lists.append(temp_cont[index*2].find_all(text=True)[0])
                res = ''
                for i in lists:
                    res+= i+'\n'
                print res
                return res

def get_10_news():
    with requests.Session() as c:
        html = c.get(URL)
        soup = BeautifulSoup(html.text)
        parse= soup.find_all("form",{"name":"ArticleList"})

        temp_cont = parse[0].find_all("a",{"class":"m-tcol-c"})
        msg = 'o 최근 채용소식\n'
        for index, node in enumerate(temp_cont):
            if index%2==0:
                msg+='- '+node.find_all(text=True)[0]+'\n'

        return msg 
