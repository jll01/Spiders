#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   douyuapp.py
# @Time    :   2019/6/24 19:28
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import requests
import json
import time
import pymysql


class DouYu(object):
    def __init__(self):
        self.offset = 0
        self.url = 'http://capi.douyucdn.cn/api/v1/live?limit=20&offset=%d'
        self.headers = {
            'User-Agent': 'android/5.9.4 (android 5.1.1; ; HUAWEI+MLA-AL10)',
        }
        self.connect = pymysql.connect(host='localhost',port=3306,db='scrapytest',user='root',passwd='0000')
        self.cur = self.connect.cursor()

    def get_info(self):
        while True:
            url = self.url % self.offset
            res = requests.get(url, headers=self.headers).text
            contents = json.loads(res).get('data')
            if len(contents) != 0:
                for content in contents:
                    con = {}
                    con['room_id'] = int(content.get('room_id'))
                    con['nickname'] = content.get('nickname')
                    con['avatar'] = content.get('avatar')
                    con['room_name'] = content.get('room_name')
                    con['show_status'] = content.get('show_status')
                    if con['show_status'] == '1':
                        con['show_status'] = '在线'
                    else:
                        con['show_status'] = '离线'
                    show_time = content.get('show_time')
                    con['show_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(show_time)))
                    con['game_name'] = content.get('game_name')
                    con['fans'] = int(content.get('fans'))
                    con['room_url'] = 'https://www.douyu.com/%s' % con['room_id']
                    con['online'] = int(content.get('online'))

                    print((con['room_id'],con['nickname'],con['game_name'],con['room_name'],con['online']))

                    self.save_data(con)

                self.offset += 20
            else:
                break

    def save_data(self,item):
        self.cur.execute(
            """insert into douyu (room_id,nickname,avatar,room_name,show_status,show_time,game_name,fans,room_url,online) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (item['room_id'],
             item['nickname'],
             item['avatar'],
             item['room_name'],
             item['show_status'],
             item['show_time'],
             item['game_name'],
             item['fans'],
             item['room_url'],
             item['online']
             ))
        self.connect.commit()

    def main(self):
        self.get_info()


if __name__ == '__main__':
    dy = DouYu()
    dy.main()
