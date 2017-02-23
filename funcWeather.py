#-*- coding: utf-8 -*-
import requests
import json
import sys

import mappingList  as m
import info

reload(sys)
sys.setdefaultencoding('utf-8')


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def weather(city):

    js = get_json_from_url('http://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&APPID='+info.W_KEY)
    js_forecast = get_json_from_url('http://api.openweathermap.org/data/2.5/forecast?q='+city+'&APPID='+info.W_KEY)

    res = { 'weather': js["weather"][0]["main"]
            , 'weather_forecast': js_forecast["list"][2]["weather"][0]["main"]
            , 'temp' : js["main"]["temp"]
            , 'temp_min' : js["main"]["temp_min"]
            , 'temp_max' : js["main"]["temp_max"]
            , 
            }
    return res

def make_weather_msg(city='Seoul'):
    msg = '아침 날씨 안내입니다.\n\n'
    if city == 'all':
        for l in m.match_city_list:
            val = weather(l)
            msg+= 'o '+m.match_city_list[l]+' 날씨\n'
            msg+= '날씨 : '+m.match_weather_list[val['weather']]+'('+m.match_weather_list[val['weather_forecast']]+')\n기온 : '+str(val['temp'])+'('+str(val['temp_min'])+'/'+str(val['temp_max'])+')\n'
    else:
        val = weather(city)
        msg = m.match_city_list[city]+' 날씨 안내입니다.\n'
        msg+= '날씨 : '+m.match_weather_list[val['weather']]+'('+m.match_weather_list[val['weather_forecast']]+'), 기온 : '+str(val['temp'])+'('+str(val['temp_min'])+'/'+str(val['temp_max'])+')'

    return msg

