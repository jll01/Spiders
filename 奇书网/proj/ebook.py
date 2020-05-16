#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   ebook.py
# @Time    :   2019/9/2 9:37
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import urllib3

from lxml import etree
from proj.tasks import get_content


class qishuebook(object):
    '''奇书网小说爬虫'''
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"
        }
        self.start_url = 'https://www.qisuu.la'
        # 存储分类的url
        self.savestarturl = []

    def startrequests(self):
        '''获取起始页分类的链接和名称'''
        page = requests.get(self.start_url, headers=self.headers, verify=False, timeout=10).text
        page_content = etree.HTML(page)
        classifyurls = page_content.xpath('//div[@class="wrap header"]/div/a/@href')
        titles = page_content.xpath('//div[@class="wrap header"]/div/a/text()')

        for title, url in zip(titles,classifyurls):
            item = {}
            item[title] = self.start_url + url
            self.savestarturl.append(item)

        get_content.delay(self.savestarturl[1:])

    def main(self):
        self.startrequests()
        print('所有信息提取完成！')


if __name__ == '__main__':

    urllib3.disable_warnings()

    eb = qishuebook()
    eb.main()
