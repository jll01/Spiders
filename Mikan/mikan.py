#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   mikan.py
# @Time    :   2020/6/8 18:04
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import redis

from fake_useragent import UserAgent
from lxml import etree


class MiKan(object):
    def __init__(self):
        self.url = '''https://mikanani.me/Home/Classic/{}'''
        self.page_num = 1
        self.add_url = '''https://mikanani.me/{}'''
        self.pool = redis.ConnectionPool(host='192.168.1.102', port=6379, db=6)
        self.red = redis.Redis(connection_pool=self.pool)

    def get_page(self):
        while True:
            try:
                page = requests.get(self.url.format(self.page_num), headers={'User-Agent': UserAgent(verify_ssl=False).random}).text
                lxml_page = etree.HTML(page)
                all_contents = lxml_page.xpath('//div[@id="sk-body"]/table/tbody/tr')
                if not all_contents:
                    raise Exception('该请求网址下所有页码获取完成！')
            except Exception as e:
                print(e)
                break
            else:
                for all_content in all_contents:
                    item = dict()
                    item['update_time'] = self.join2str(all_content.xpath('./td[1]/text()'))
                    item['fansub_group'] = self.join2str(all_content.xpath('./td[2]//text()'))
                    item['fanzu_url'] = self.add_url.format(self.join2str(all_content.xpath('./td[3]/a[1]/@href')))
                    item['fanzu_name'] = self.join2str(all_content.xpath('./td[3]/a[1]/text()'))
                    item['magnet'] = self.join2str(all_content.xpath('./td[3]/a[2]/@data-clipboard-text'))
                    item['size'] = self.join2str(all_content.xpath('./td[4]/text()'))
                    item['download'] = self.add_url.format(self.join2str(all_content.xpath('./td[5]/a/@href')))
                    print(item)
                    self.save2redis(item)
                self.page_num += 1
                time.sleep(random.uniform(1, 1.5))

    @staticmethod
    def join2str(inner):
        return ''.join(inner).replace('\r\n', '').strip()

    def save2redis(self, item):
        self.red.hmset(int(time.time() * 1000), item)

    def main(self):
        self.get_page()


if __name__ == '__main__':
    mk = MiKan()
    mk.main()
