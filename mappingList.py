#-*- coding: utf-8 -*-
import sys
import collections
reload(sys)
sys.setdefaultencoding('utf-8')

match_city_list = {
        'Seoul'     :   '서울'
        , 'Busan'   :   '부산'
        , 'Daegu'   :   '대구'
        , 'Naju'    :   '나주'
        }

match_city_list = collections.OrderedDict(match_city_list.items())

match_weather_list = {
        'Clear'     :   '맑음'
        , 'Rain'    :   '비'
        , 'Clouds'  :   '구름'
        , 'Snow'    :   '눈'
        , 'Haze'    :   '안개' 
        }


