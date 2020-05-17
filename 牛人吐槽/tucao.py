#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   tucao.py
# @Time    :   2020/1/21 17:25
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import fake_useragent
import requests
import time
import random
import re
import json

from lxml import etree


class TuCao(object):
    def __init__(self):
        self.urls = 'http://www.bullpeople.cn/tucao/page_{}.html'
        self.num = 2
        self.useragent = fake_useragent.UserAgent()

    def getpage(self):
        while self.num <= 10:
            headers = {
                'User-Agent': self.useragent.random
            }
            html = requests.get(self.urls.format(self.num), headers=headers).text
            etree_html = etree.HTML(html)
            urls = etree_html.xpath('//ul[@id="detail"]/li/a/@href')
            titles = etree_html.xpath('//ul[@id="detail"]/li/a/@title')
            agrees = etree_html.xpath('//ul[@id="detail"]/li/div/span[@class="cursor"]/span/text()')
            comments = etree_html.xpath('//ul[@id="detail"]/li/div/a[@class="mleft"]/text()')
            contents = etree_html.xpath('//ul[@id="detail"]/li/a/text()')

            detail = zip(urls, titles, agrees, comments, contents)
            for url, title, agree, comment, content in detail:
                item = {}
                item['url'] = url
                item['title'] = title
                agree = self.str2num(re.findall(r'\d+', str(agree)))
                item['agree'] = agree
                comment = self.str2num(re.findall(r'\d+', str(comments)))
                item['comment'] = comment
                item['content'] = content
                print(url, title, agree, comment, content)
                self.save_text(item)

            time.sleep(random.uniform(0, 3))
            self.num += 1

    def save_text(self, item):
        with open('牛人吐槽.json', 'a', encoding='utf-8') as file:
            file.write(json.dumps(item, ensure_ascii=False) + '\n')

    @staticmethod
    def str2num(s):
        res = ''.join(s)
        if len(res):
            return eval(res)
        else:
            return 0

    def main(self):
        self.getpage()


if __name__ == '__main__':
    tc = TuCao()
    tc.main()
