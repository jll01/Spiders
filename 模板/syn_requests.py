#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   syn_requests.py
# @Time    :   2020/6/3 11:25
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import urllib3

from lxml import etree
from fake_useragent import UserAgent


class Spiders(object):
    def __init__(self):
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        self.ua = UserAgent(verify_ssl=False)
        self.page = 1

    def get_data(self):
        while True:
            headers = {
                'User-Agent': self.ua.random
            }
            request = requests.get(self.base_url.format(self.page), headers=headers, verify=False)
            if request.status_code == 200:
                html = etree.HTML(request.text)
                contents = html.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
                for content in contents:
                    item = dict()

                    item['nickname'] = self.join_list(content.xpath('./div[1]/div/a/i/text()'))
                    item['content'] = self.join_list(content.xpath('./p[@class="fonts"]/a/text()'))
                    item['support'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                    item['not_support'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                    item['collect'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                    item['message'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))
                    item['share'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()')))

                    print(item)
                    # 保存数据
                    # mysql_save_data(self.connect, self.cur, 'test', item)
                self.page += 1
                time.sleep(random.uniform(1, 3))
            else:
                break

    @staticmethod
    def join_list(res):
        return ''.join(res)

    def main(self):
        self.get_data()


if __name__ == '__main__':

    urllib3.disable_warnings()

    sp = Spiders()
    sp.main()
