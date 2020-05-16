#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   bilibili.py
# @Time    :   2019/10/16 21:53
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import time
import urllib3
import random
import math
import pymysql

from threading import Thread, Lock


class Bilibili(object):
    def __init__(self):
        # 获取视频的aid和cid参数
        self.url = 'https://api.bilibili.com/x/web-interface/newlist?rid=153&type=0&pn={}&ps=20&jsonp=jsonp&_={}'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
        }
        self.page = 1
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()
        self.lock = Lock()

    def getvideo(self):
        '''获取视频相关信息'''
        while True:
            now = time.time() * 1000
            contents_jdon = requests.get(self.url.format(self.page, now), headers=self.headers).json()
            try:
                contents = contents_jdon.get('data').get('archives')
                count = contents_jdon.get('data').get('page').get('count')
            except Exception as e:
                print('提取错误！{}'.format(e))
                break
            else:
                ths = []
                for content in contents:
                    item = {}

                    item['aid'] = content.get('aid', 0)
                    item['cid'] = content.get('cid', 0)
                    item['tname'] = content.get('tname', 'Null')  # 视频属于哪一类型
                    item['title'] = content.get('title', 'Null')  # 标题
                    item['pubdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                    time.localtime(content.get('pubdate', now)))  # 发布时间
                    item['desc_v'] = content.get('desc', 'Null')  # 视频描述
                    redirect_url = content.get('redirect_url', 'Null')  # 视频url
                    if redirect_url != 'Null':
                        item['redirect_url'] = redirect_url
                    else:
                        item['redirect_url'] = 'https://www.bilibili.com/video/av{}/'.format(item['aid'])  # 视频url

                    stat = content.get('stat', 'Null')
                    item['view_v'] = stat.get('view', 0)  # 观看人数
                    item['danmaku'] = stat.get('danmaku', 0)  # 弹幕数量
                    item['favorite'] = stat.get('favorite', 0)  # 喜欢数
                    item['coin'] = stat.get('coin', 0)  # 金币
                    item['share'] = stat.get('share', 0)  # 分享
                    item['like_v'] = stat.get('like', 0)  # 收藏

                    print(item)
                    self.save_video(item)
                    # self.getdanmu(item['aid'],item['cid'])
                    # t = Thread(target=self.getdanmu, args=(item['aid'], item['cid']))   # 多线程
                    #
                    # t.start()
                    # ths.append(t)

                # for i in ths:
                #     i.join()
                if self.page >= math.ceil(count / 20):
                    break
            finally:
                self.page += 1
                time.sleep(random.uniform(3, 5))

    def getdanmu(self, aid, cid):
        '''获取弹幕内容'''
        url = 'https://api.bilibili.com/x/v1/dm/list.so?oid={}'.format(cid)

        danmu = requests.get(url, headers=self.headers).content  # xml格式
        danmu_items = re.findall(r'<d\s+p=\"(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\">(.*?)</d>',
                                 danmu.decode('utf-8'))  # 正则匹配弹幕参数
        if len(danmu_items) != 0:
            for danmu_item in danmu_items:
                item_d = {}

                item_d['aid'] = aid
                item_d['cid'] = cid
                item_d['danmu_time'] = eval(danmu_item[0])  # 弹幕出现的时间进度位置
                item_d['danmu_moshi'] = eval(danmu_item[1])  # 弹幕模式
                item_d['danmu_size'] = eval(danmu_item[2])  # 字体大小
                item_d['danmu_color'] = eval(danmu_item[3])  # 颜色
                item_d['send_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(danmu_item[4])))  # 发布弹幕时间
                item_d['danmu_pool'] = eval(danmu_item[5])  # 弹幕池
                item_d['send_id'] = danmu_item[6]  # 发送弹幕id
                item_d['rowid'] = eval(danmu_item[7])
                item_d['content'] = danmu_item[8]  # 内容

                print(item_d)
                self.save_danmu(item_d)

    def save_video(self, item):
        '''保存视频相关信息'''
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into bili_video (aid,cid,tname,title,pubdate,desc_v,redirect_url,view_v,danmaku,favorite,coin,share,like_v) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['aid'],
                    item['cid'],
                    item['tname'],
                    item['title'],
                    item['pubdate'],
                    item['desc_v'],
                    item['redirect_url'],
                    item['view_v'],
                    item['danmaku'],
                    item['favorite'],
                    item['coin'],
                    item['share'],
                    item['like_v'],
                ))
        except Exception as e:
            print('一条数据插入错误!{}'.format(e))
        else:
            self.connect.commit()
        self.lock.release()

    def save_danmu(self, item):
        '''保存弹幕相关'''
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into bili_danmu (aid,cid,danmu_time,danmu_moshi,danmu_size,danmu_color,send_time,danmu_pool,send_id,rowid,content) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['aid'],
                    item['cid'],
                    item['danmu_time'],
                    item['danmu_moshi'],
                    item['danmu_size'],
                    item['danmu_color'],
                    item['send_time'],
                    item['danmu_pool'],
                    item['send_id'],
                    item['rowid'],
                    item['content'],
                ))
        except Exception as e:
            print('一条数据插入错误!{}'.format(e))
        else:
            self.connect.commit()
        self.lock.release()

    def main(self):
        self.getvideo()


if __name__ == '__main__':
    urllib3.disable_warnings()

    bili = Bilibili()
    bili.main()
