#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   budejie.py
# @Time    :   2019/9/16 10:02
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import urllib3
import random
import json


class BuDeJie(object):
    def __init__(self,page):
        self.url = 'http://e.api.budejie.com/v2/topic/list/29/28159405-29775259/budejie-android-8.1.8/0-25.json'
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        }
        self.start = 1
        self.page =page

    def request_url(self):
        while self.start <= self.page:
            req = requests.get(self.url,headers=self.headers).json()
            contents = req.get('list','NULL')
            if contents != 'NULL':
                for content in contents:
                    item = {}
                    user = content.get('u', 'NULL')
                    item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    if user != 'NULL':
                        item['name'] = user.get('name', 'NULL')
                        item['uid'] = self.changenum(user.get('uid', 'NULL'))
                        item['header'] = user.get('header', [''])[0]

                    item['id'] = self.changenum(content.get('id', 'NULL'))
                    item['share_url'] = content.get('share_url','NULL')
                    item['text'] = content.get('text','NULL')
                    item['passtime'] = content.get('passtime','NULL')
                    item['up'] = self.changenum(content.get('up','NULL'))
                    item['down'] = self.changenum(content.get('down','NULL'))
                    item['comment'] = self.changenum(content.get('comment','NULL'))

                    print(item)
                    self.saveitem(item)

            print('----------第{}页以区完成！----------'.format(self.start))
            time.sleep(random.uniform(2,4))
            self.start+= 1

    def changenum(self,res):
        if res != 'NULL':
            return int(res)
        else:
            return 'NULL'

    def saveitem(self,item):
        with open('budejie.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


    def main(self):
        self.request_url()


if __name__ == '__main__':
    urllib3.disable_warnings()

    try:
        page= int(input('请输入要提取的页数：'))
    except:
        page = 1
    bdj = BuDeJie(page)
    bdj.main()



