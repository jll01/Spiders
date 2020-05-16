#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   moviecomment.py
# @Time    :   2019/10/8 16:33
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import pymysql


class Comment(object):

    def __init__(self):

        self.url = 'http://m.maoyan.com/mmdb/comments/movie/1277939.json?v=yes&offset=0&startTime={}'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
        }

        self.connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cur = self.connect.cursor()

    def get(self):
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        end_time = '2019-09-30 09:00:00'
        while start_time >= end_time:
            req = requests.get(self.url.format(start_time.replace(' ', '%20')),headers=self.headers).json()
            contents = req.get('cmts')
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
                # item['commentTime'] = content.get('startTime', 'Null')
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

                print(item)
                self.saveitem(item)

            last_time = contents[-1].get('startTime')
            start_time = last_time[:-2] + str(int(last_time[-2:]) - 1)

            time.sleep(random.uniform(1,3))

    def saveitem(self,item):
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

    def main(self):
        self.get()


if __name__ == '__main__':

    comment = Comment()
    comment.main()
