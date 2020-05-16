#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   hangqing.py
# @Time    :   2019/7/13 12:43
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100,  LJL
# @Desc    :   None

# here put the import lib

import requests
import time
import random
import re
import json
import redis
import pymysql
import urllib3


class DongFang(object):
    def __init__(self):
        self.session = requests.session()
        self.agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        ]
        self.redis = redis.StrictRedis(host='localhost', port=6379,db=2)
        self.connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cursor = self.connect.cursor()
        self.headers = {
            'User-Agent': random.choice(self.agent),
        }
        self.page = 1
        self.url_list = [
            'http://2.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112405362630328850491_1563002247934&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://94.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407165873795760787_1563008222011&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://72.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407165873795760787_1563008222009&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://38.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407165873795760787_1563008222009&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f26&fs=m:0+f:8,m:1+f:8&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://26.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407165873795760787_1563008222009&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:13&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://26.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407165873795760787_1563008222009&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://27.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407165873795760787_1563008222009&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1{}',
            'http://2.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409791820052890827_1563010704738&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f26&fs=b:BK0707&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://94.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409791820052890827_1563010704738&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f26&fs=b:BK0804&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://33.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409791820052890827_1563010704738&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:7,m:1+t:3&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}',
            'http://64.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409791820052890827_1563010704738&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f199&fs=m:1+b:BK0498&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f201,f202,f203,f196,f197,f199,f195,f200&_={}',
            'http://90.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409791820052890827_1563010704738&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f199&fs=m:0+b:BK0498&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f201,f202,f203,f196,f197,f199,f195,f200&_={}',
            'http://37.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409791820052890827_1563010704738&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+f:4,m:1+f:4&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={}'
        ]

    def get_data(self):
        for url in self.url_list:
            while True:
                url_page = url.format(self.page, int(time.time() * 1000))
                con = self.session.get(url_page,headers=self.headers,verify=False).text
                data = re.findall(r'jQuery.*?\((.*?)\)',con)
                json_connects = json.loads(data[0])

                try:
                    connects = json_connects['data']['diff']
                except Exception as e:
                    print('出错了{}'.format(e))
                    break
                else:
                    for connect in connects:
                        time.sleep(0.3)
                        item = {}
                        item['code'] = connect['f12'] # 代码
                        item['name'] = connect['f14']  # 名称
                        item['lasted'] = connect['f2']  # 最新价
                        item['changePercent'] = connect['f3'] # 涨跌幅
                        item['changeprice'] = connect['f4']  # 涨跌额
                        item['okvolume'] = connect['f5']  # 成交量
                        item['okamount'] = connect['f6']  # 成交额
                        item['amplitude'] = connect['f7'] # 振幅
                        item['high'] = connect['f15']  # 最高
                        item['low'] = connect['f16']  # 最低
                        item['today'] = connect['f17']  # 今开
                        item['previousClose'] = connect['f18']  # 昨收
                        item['volumeRate'] = connect['f10']  # 量比
                        item['turnoverRate'] = connect['f8']  # 换手率
                        item['peration'] = connect['f9']  # 市盈率
                        item['pb'] = connect['f23']  # 市净率

                        print(item)

                        with open('gupiao.json', 'a', encoding='utf-8') as f:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')

                        self.save_redis(item)
                        self.save_mysql(item)

                time.sleep(1)
                self.page += 1

    def save_redis(self,item):
        self.redis.hmset(int(time.time()*1000), item)

    def save_mysql(self,item):
        self.cursor.execute(
            """insert into dongfang (code,name,lasted,changePercent,changeprice,okvolume,okamount,amplitude,high,low,today,previousClose,volumeRate,turnoverRate,peration,pb) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['code'],
                item['name'],
                item['lasted'],
                item['changePercent'],
                item['changeprice'],
                item['okvolume'],
                item['okamount'],
                item['amplitude'],
                item['high'],
                item['low'],
                item['today'],
                item['previousClose'],
                item['volumeRate'],
                item['turnoverRate'],
                item['peration'],
                item['pb'],
             ))
        self.connect.commit()

    def close_mysql(self):
        self.connect.close()


if __name__ == '__main__':
    urllib3.disable_warnings()
    dongfang = DongFang()
    dongfang.get_data()
    dongfang.close_mysql()