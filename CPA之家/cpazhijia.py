#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   cpazhijia.py
# @Time    :   2020/6/7 9:43
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import random
import time
import json
import pymysql
import os

from fake_useragent import UserAgent


class CPA(object):
    def __init__(self):
        self.url = '''https://www.cpajia.com/index.php?m=index&a=search'''
        self.page_num = 1
        self.commit_num = 0
        self.file = ''
        self.log = ''
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', password='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def get_json(self):
        while True:
            data = {
                'PageIndex': self.page_num,
                'args': 0
            }
            headers = {
                'Host': 'www.cpajia.com',
                'Origin': 'https://www.cpajia.com',
                'Referer': 'https://www.cpajia.com/',
                'User-Agent': UserAgent().random
            }
            try:
                source = requests.post(self.url, data=data, headers=headers)
                contents = source.json()
                if not contents[1]['id']:
                    raise Exception(f'第{self.page_num}获取失败,数据已超出！')
            except Exception as e:
                print(e)
                break
            else:
                self.get_content(contents)
                print(f'第{self.page_num}页保存完成！')
                time.sleep(random.uniform(0.8, 1.5))
                self.page_num += 1

    def get_content(self, contents):
        for content in contents[1:]:
            item = dict()

            # cpa id
            item['id'] = content.get('id', '0')
            # 用户id
            item['userid'] = content.get('userid', '0')
            # 昵称
            item['username'] = content.get('username', '').strip()
            # 名称
            item['title'] = content.get('title', '')
            # 产品要求
            item['content'] = content.get('content', '').strip()
            # 发布时间
            item['createtime'] = self.time2str(content.get('createtime', time.time()))
            # 系统
            item['platform'] = content.get('platform', '')
            # 结算方式
            item['balance'] = content.get('balance', '')
            # 数据查看
            item['dataview'] = content.get('dataview', '')
            # 数据查看
            item['company'] = content.get('company', '').strip()
            #单价（元）
            item['price'] = content.get('price', '0')
            # QQ
            item['qq'] = content.get('qq', '0')
            # 电话
            item['phone'] = content.get('phone', '0')
            # 微信号
            item['wxh'] = content.get('wxh', '0')

            print(item)
            self.save2json(item)
            self.save2mysql(item)

    @staticmethod
    def time2str(inner):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(inner)))

    def save2mysql(self, item):
        try:
            self.cur.execute(
                '''insert into cpa (id, userid, username, title, content, createtime, platform, balance, dataview, company, price, qq, phone, wxh) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (
                    item['id'],
                    item['userid'],
                    item['username'],
                    item['title'],
                    item['content'],
                    item['createtime'],
                    item['platform'],
                    item['balance'],
                    item['dataview'],
                    item['company'],
                    item['price'],
                    item['qq'],
                    item['phone'],
                    item['wxh'],
                )
            )
            self.commit_num += 1
            # self.connect.commit()
        except Exception as e:
            print(f'{item}出错了{e}')
            self.log.write(f'{item}出错了{e}' + '\n')
        else:
            if self.commit_num == 20:
                self.connect.commit()
                self.commit_num = 0

    def save2json(self, con):
        self.file.write(json.dumps(con, ensure_ascii=False) + '\n')

    def main(self):
        # if not os.path.exists('cpa.json'):
        #     os.mknod('cpa.json')

        self.file = open('cpa.json', 'w', encoding='utf-8')
        self.log = open('error.txt', 'w', encoding='utf-8')
        self.get_json()
        self.file.close()
        self.log.close()
        self.connect.commit()


if __name__ == '__main__':
    cpa = CPA()
    cpa.main()
