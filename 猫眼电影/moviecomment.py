#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   moviecomment.py
# @Time    :   2020/4/19 16:33
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import pymysql
import datetime

from threading import Thread, Lock


class Comment(object):

    def __init__(self):

        self.url = 'http://m.maoyan.com/mmdb/comments/movie/1277939.json?v=yes&offset={}&startTime={}'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
        }
        self.lock = Lock()

        self.connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cur = self.connect.cursor()

    def get(self, offset,start_time, end_time):
        while start_time >= end_time:
            url = self.url.format(offset,start_time.replace(' ', '%20'))
            # print(url)
            req = requests.get(url,headers=self.headers).json()
            contents = req.get('cmts','Null')
            if contents != 'Null':
                for content in contents:
                    item = {}
                    item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    item['commentTime'] = content.get('startTime', 'Null')
                    item['userId'] = content.get('userId', 0)
                    item['nickName'] = content.get('nickName', 'Null')
                    item['gender'] = int(content.get('gender', '0')) # 1是男，2是女，0是隐藏了性别
                    item['userLevel'] = content.get('userLevel', 0)
                    item['cityName'] = content.get('cityName', 'Null')
                    item['content'] = content.get('content', 'Null')
                    item['score'] = content.get('score', 0)
                    item['reply'] = content.get('reply', 0) # 回复
                    item['approve'] = content.get('approve', 0) # 点赞数
                    try:
                        ids= content.get('tagList', 'Null').get('fixed')[0]
                        if ids.get('id') == 1:
                            item['tagList'] = ids.get('name')
                        else:
                            item['tagList'] = '无'
                    except:
                        item['tagList'] = '无'

                    if item['commentTime'] < end_time:
                        break
                    else:
                        print(item)
                        self.saveitem(item)

                if offset == 990:
                    offset = 0
                    time_date = datetime.datetime.strptime(contents[-1].get('startTime'), '%Y-%m-%d %H:%M:%S')
                    start_time = time_date + datetime.timedelta(seconds=-1)
                    start_time = datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
                else:
                    offset += 15
                    time.sleep(random.uniform(1,3))
            else:
                break

    def multiget(self):
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        dates = [
            (start_time, '2019-10-11 00:00:00'),
            ('2019-10-10 23:59:59', '2019-10-10 00:00:00'),
            ('2019-10-09 23:59:59', '2019-10-09 00:00:00'),
            ('2019-10-08 23:59:59', '2019-10-08 00:00:00'),
            ('2019-10-07 23:59:59', '2019-10-07 00:00:00'),
            ('2019-10-06 23:59:59', '2019-10-06 00:00:00'),
            ('2019-10-05 23:59:59', '2019-10-05 00:00:00'),
            ('2019-10-04 23:59:59', '2019-10-04 00:00:00'),
            ('2019-10-03 23:59:59', '2019-10-03 00:00:00'),
            ('2019-10-02 23:59:59', '2019-10-02 00:00:00'),
            ('2019-10-01 23:59:59', '2019-10-01 00:00:00'),
            ('2019-09-30 23:59:59', '2019-09-30 09:00:00'),
        ]
        ths = []
        for date in dates:
            t = Thread(target=self.get,args=(0,date[0],date[1]))
            t.start()
            ths.append(t)

        for th in ths:
            th.join()

    def saveitem(self,item):
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into moviecomment (spidertime,commentTime,userId,nickName,gender,userLevel,cityName,content,score,reply,approve,tagList) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['spidertime'],
                    item['commentTime'],
                    item['userId'],
                    item['nickName'],
                    item['gender'],
                    item['userLevel'],
                    item['cityName'],
                    item['content'],
                    item['score'],
                    item['reply'],
                    item['approve'],
                    item['tagList'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print('一条数据出错了！{}'.format(e))
        self.lock.release()

    def main(self):
        self.multiget()


if __name__ == '__main__':

    comment = Comment()
    comment.main()
