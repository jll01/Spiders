#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   tasks.py
# @Time    :   2020/3/1 16:12
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import urllib3
import pymysql
import json
import random

from celery import group
from proj.app_test import app


urllib3.disable_warnings()

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
}
connect = pymysql.connect(host='192.168.1.103',port=3306,user='root',passwd='0000',db='scrapytest')
cur = connect.cursor()


# trail=True如果启用，请求将跟踪由该任务启动的子任务，并且此信息将与结果（result.children）一起发送。
@app.task(trail=True)
def get_content(urls):
    '''并行调用任务,group一次创建多个任务'''
    group(C.s(url) for url in urls)()


@app.task(trail=True)
def C(url):
    '''返回此任务的签名对象，包装单个任务调用的参数和执行选项。'''
    parser.delay(url)


@app.task(trail=True)
def parser(url):
    '''获取每个分类中具体书籍的详情url'''
    json_comment = requests.get(url, headers=headers, verify=False).text
    comments = json.loads(json_comment)
    try:
        commentlist = comments.get('comment', 'NULL').get('commentlist', 'NULL')
    except Exception as e:
        pass
    else:
        if commentlist != None:
            for comment in commentlist:
                item = dict()
                item['nick'] = comment.get('nick', 'Null')
                item['praisenum'] = comment.get('praisenum', 0)
                item['content'] = comment.get('rootcommentcontent', 'Null')
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment.get('time', int(time.time()))))
                item['qq'] = eval(comment.get('uin', 'Null'))  # QQ号

                try:
                    middlecomments = comment.get('middlecommentcontent', 'Null')
                    mid = []
                    for middlecomment in middlecomments:
                        item_mid = {}
                        item_mid['replyednick'] = middlecomment.get('replyednick', 'Null').replace('@', '')
                        item_mid['replyeduin'] = eval(middlecomment.get('replyeduin', 'Null'))
                        item_mid['subcommentcontent'] = middlecomment.get('subcommentcontent', 'Null')

                        mid.append(item_mid)

                    item['middlecomments'] = str(mid)
                except:
                    item['middlecomments'] = ''
                finally:
                    print(item)
                    savecomment(item)
            time.sleep(random.uniform(0.5,1.5))


def savecomment(item):
    try:
        cur.execute(
            '''insert into qqmusic (nick,praisenum,content,time,qq,middlecomments) values (%s,%s,%s,%s,%s,%s)''',
            (
                item['nick'],
                item['praisenum'],
                item['content'],
                item['time'],
                item['qq'],
                item['middlecomments']
            )
        )
        connect.commit()
    except Exception as e:
        print('出错：{}'.format(e))
