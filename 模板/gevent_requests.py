#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   gevent_requests.py
# @Time    :   2020/6/8 10:13
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from gevent import monkey
monkey.patch_all()

import gevent
import requests
import urllib3
import time

from lxml import etree
from fake_useragent import UserAgent
from gevent import queue


# 计时装饰器
def timer(inner):
    def func(self, *args, **kwargs):
        start = time.time()
        inner(self, *args, **kwargs)
        print("complete in {} seconds".format(time.time() - start))

    return func


class Crawl(object):
    """
        下面使用的是Queue存储url， 还可以先将所有url获取存储到列表中在使用spawn
    """
    def __init__(self, thnum, pagenum):
        self.thnum = thnum
        self.pagenum = pagenum
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        self.ua = UserAgent(verify_ssl=False)

    def put_url(self, urls):
        for i in range(1, self.pagenum+1):
            urls.put(self.base_url.format(i))

    def get_page(self, url, url_queue):
        headers = {
            'User-Agent': self.ua.random
        }
        request = requests.get(url, headers=headers, verify=False)
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
        else:
            url_queue.put(url)

    @staticmethod
    def join_list(res):
        return ''.join(res)

    @timer
    def main(self):
        url_queue = queue.Queue()
        self.put_url(url_queue)

        threads = []
        while not url_queue.empty():
            url = url_queue.get()
            threads.append(gevent.spawn(self.get_page, url, url_queue))

        gevent.joinall(threads)


if __name__ == '__main__':

    urllib3.disable_warnings()

    threadNum = 3
    pageNum = 5
    cra = Crawl(threadNum, pageNum)
    cra.main()
