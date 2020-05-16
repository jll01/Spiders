#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   douyin.py
# @Time    :   2019/6/24 14:50
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import requests
import json
import time
import os
import pymysql

from threading import Thread


class DouYin(object):
    def __init__(self):
        self.filepath = r'E:\练习\Python\高级教程\爬虫\练习\APP抓包\抖音\抖音数据爬取'
        self.pathinfo = r'E:\练习\Python\高级教程\爬虫\练习\APP抓包\抖音\视频存放'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)",
        }
        self.connect = pymysql.connect(host='localhost',port=3306,db='scrapytest',user='root',passwd='0000')
        self.cur = self.connect.cursor()

    def str2int(self,str_int):
        if str_int:
            return int(str_int)
        else:
            return 0

    def run(self):
        while True:
            filenames = os.listdir(self.filepath)
            if len(filenames) != 0:
                # time.sleep(2)
                for filename in filenames:
                    file = os.path.join(self.filepath, filename)
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            contents = json.loads(f.read())
                        os.remove(file)
                        douyin_info = contents.get('aweme_list')
                        for info in douyin_info:
                            down = Thread(target=self.get_info, args=(info,))
                            down.start()
                            down.join()
                    except Exception as e:
                        print('出错了！{}'.format(e))

            else:
                time.sleep(1)
                print('{}    目录暂时为空！'.format(self.filepath))

    def get_info(self,info):
        people_info = {}
        people_info['video_id'] = info.get('aweme_id')
        people_info['desc'] = info.get('desc')
        people_info['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.get('create_time')))

        statistics = info.get('statistics')
        people_info['comment'] = self.str2int(statistics.get('comment_count'))
        people_info['thumbsup'] = self.str2int(statistics.get('digg_count'))
        people_info['download'] = self.str2int(statistics.get('download_count'))
        people_info['share'] = self.str2int(statistics.get('share_count'))

        video = info.get('video')
        play_addr = video.get('play_addr')
        url_list = play_addr.get('url_list')
        people_info['url'] = url_list[0]

        author = info.get('author')
        people_info['nick'] = author.get('nickname')
        if author.get('gender') == 2:
            people_info['gender'] = '女'
        else:
            people_info['gender'] = '男'

        people_info['sign'] = author.get('signature')
        people_info['douyin_id'] = author.get('unique_id')
        people_info['birthday'] = author.get('birthday')

        print((people_info['nick'],people_info['gender'],people_info['birthday']))
        self.save_info(people_info)
        # self.download(people_info['url'],people_info['video_id'])

    def save_info(self,item):
        self.cur.execute(
            """insert into douyin (video_id,desc_douyin,start_date,comment,thumbsup,download,share,nick,gender,sign,douyin_id,birthday) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (self.str2int(item['video_id']),
             item['desc'],
             item['date'],
             item['comment'],
             item['thumbsup'],
             item['download'],
             item['share'],
             item['nick'],
             item['gender'],
             item['sign'],
             item['douyin_id'],
             item['birthday'],
             ))
        self.connect.commit()

    def download(self,url,video_id):
        res = requests.get(url, headers=self.headers, stream=True)

        temp_size = 0
        if res.status_code == 200:
            with open(os.path.join(self.pathinfo,video_id+'.mp4'), 'wb') as file:
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        temp_size += len(chunk)
                        file.write(chunk)
                        file.flush()  # 刷新缓存
                print("%s下载完成！" % (video_id+'.mp4'))

    def main(self):
        self.run()


if __name__ == '__main__':
    douyin = DouYin()
    douyin.main()
