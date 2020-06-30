#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   selenium_spider.py
# @Time    :   2020/6/11 17:04
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import time
import random

from lxml import etree
from selenium import webdriver


class Spiders(object):
    def __init__(self):
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        self.page = 1
        # chrome_drive = r'D:\Soft\Browser\Google\Chrome\Application\chromedriver.exe'
        # self.driver = webdriver.Chrome(executable_path=chrome_drive)
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def get_data(self):
        while True:
            url = self.base_url.format(self.page)
            self.driver.get(url)
            time.sleep(random.uniform(1, 3))
            html = etree.HTML(self.driver.page_source)
            contents = html.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
            if len(contents) != 0:
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
            else:
                break

    @staticmethod
    def join_list(res):
        return ''.join(res)

    def main(self):
        self.get_data()


if __name__ == '__main__':

    sp = Spiders()
    sp.main()
