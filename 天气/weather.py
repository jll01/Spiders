#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   weather.py
# @Time    :   2020/1/19 15:44
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import time
import random
import json
import os
import pandas as pd
import pymysql
import math

from threading import Thread, Lock


class Weather(object):
    def __init__(self, cid, start, end):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36", 
        }
        self.cid = cid
        self.start = start
        self.end = end
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()
        self.lock = Lock()

    def request(self):
        dates = pd.period_range(self.start, self.end, freq='M')

        date_list = []
        urllist = []
        for date in dates:
            date_list.append(str(date).replace('-', ''))

        for date in date_list:
            if int(date) < 201603:
                if int(date[-2:]) < 10:
                    date = date[:4] + str(int(date[-2:]))

                url = 'http://tianqi.2345.com/t/wea_history/js/{}_{}.js'.format(self.cid, date)
            else:
                url = 'http://tianqi.2345.com/t/wea_history/js/{}/{}_{}.js'.format(date, self.cid, date)

            urllist.append(url)

        for i in range(math.ceil(len(urllist)/5)):
            thread = []
            for url in urllist[i*5:(i+1)*5]:
                th = Thread(target=self.getdata, args=(url, ))
                th.start()
                thread.append(th)

            for thr in thread:
                thr.join()

    def getdata(self, url):
        try:
            req = requests.get(url, headers=self.headers).text
            datas = re.findall(r'(\{ymd:.*?\})', req)
            for data in datas:
                data = eval(data.replace('ymd', '"ymd"').replace('bWendu', '"bWendu"').replace('yWendu', '"yWendu"').replace('tianqi', '"tianqi"').replace('fengxiang', '"fengxiang"').replace('fengli', '"fengli"').replace('aqi:', '"aqi":').replace('aqiInfo:', '"aqiInfo":').replace('aqiLevel:', '"aqiLevel":'))
                item = dict()
                item['date'] = data.get('ymd', '')
                item['bWendu'] = eval(data.get('bWendu', '0').replace('℃', ''))
                item['yWendu'] = eval(data.get('yWendu', '0').replace('℃', ''))
                item['tianqi'] = data.get('tianqi', '')
                item['fengxiang'] = data.get('fengxiang', '')
                item['fengli'] = data.get('fengli', '')
                item['aqi'] = eval(data.get('aqi', '0'))
                item['aqiInfo'] = data.get('aqiInfo', '')
                item['aqiLevel'] = eval(data.get('aqiLevel', '0'))

                print(item)
                self.saveitem(item)
        except Exception as e:
            print('提取数据错误！')
        finally:
            time.sleep(random.uniform(1, 2))

    def saveitem(self, item):
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into weather (date, bWendu, yWendu, tianqi, fengxiang, fengli, aqi, aqiInfo, aqiLevel) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                (
                    item['date'], 
                    item['bWendu'], 
                    item['yWendu'], 
                    item['tianqi'], 
                    item['fengxiang'], 
                    item['fengli'], 
                    item['aqi'], 
                    item['aqiInfo'], 
                    item['aqiLevel'], 
                )
            )
            self.connect.commit()
        except Exception as e:
            print('一条数据保存出错了{}！'.format(e))

        self.lock.release()

    def main(self):
        self.request()


def cityid():

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36", 
    }
    url = 'http://tianqi.2345.com/js/citySelectData.js'
    city = requests.get(url, headers=headers).text
    # 获取第二部分的字符
    city2 = city.split('var provqx=new Array();')[1]

    # 每个市管辖地区
    city3 = re.findall(r"\'(.*?)\'", city2)
    city_list = []
    for ci in city3:
        datas = re.findall(r'(\d+)-\w+\s+(.*?)-(\d+)', ci)
        city_id_list = []
        item = {}
        for data in datas:
            city_id_list.append({data[1]:int(data[0])})
            if data[0] == data[2]:
                item[data[1]] = city_id_list

        city_list.append(item)

    with open('cityid.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'city':city_list}, ensure_ascii=False))


if __name__ == '__main__':
    if not os.path.exists('cityid.json'):
        print('请稍等，正在获取城市id！')
        cityid()

    with open('cityid.json', 'r', encoding='utf-8') as f:
        readid = f.read()

    id_json= json.loads(readid)
    # 含有字典的列表
    ids = id_json.get('city')

    flag = 0
    # 北京id
    city_id = 54511

    city_shi = input('请输入要查找的城市(市级)名称(格式:西安)：')
    flag_judje = 0
    for ci in ids:
        judje = ci.get(city_shi)
        if judje:
            for city in judje:
                for key, value in city.items():
                    print(key, end=' ')
            print()
            city_xian = input('请选择区县级城市：')
            for city in judje:
                for key, value in city.items():
                    if key == city_xian.strip():
                        city_id = value
                        flag = 1

            if flag == 0:
                print('未查到你输入的城市{}！'.format(city_xian))
            else:
                start = input('请输入起始时间(格式:201901)：')
                end = input('请输入结束时间(格式:201901)：')
                wea = Weather(city_id, start, end)
                wea.main()

            flag_judje = 1
    if flag_judje == 0:
        print('未找到你要查找的城市，请检查输入！')