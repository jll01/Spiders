#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   multiprocessing_pool_requests.py
# @Time    :   2020/6/7 15:18
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import urllib3
import time
import queue

from lxml import etree
from fake_useragent import UserAgent
from multiprocessing import Pool, Manager
from concurrent.futures import ProcessPoolExecutor

urllib3.disable_warnings()


# 计时装饰器
def timer(inner):
    def func(self, *args, **kwargs):
        start = time.time()
        inner(self, *args, **kwargs)
        print("complete in {} seconds".format(time.time() - start))

    return func


class Crawl(object):
    """
        使用concurrent.futures中的ProcessPoolExecutor进程池模块爬虫
    """
    def __init__(self, thnum, pagenum):
        self.thnum = thnum
        self.pagenum = pagenum

    def get_page(self, url):
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random
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

    @staticmethod
    def join_list(res):
        return ''.join(res)

    @timer
    def main(self):
        q = queue.Queue()
        base_url = 'https://www.xiaohua.com/duanzi?page={}'
        urls = [base_url.format(i) for i in range(1, self.pagenum + 1)]
        # [q.put(base_url.format(i)) for i in range(1, self.pagenum + 1)]
        with ProcessPoolExecutor() as pool:
            # while not q.empty():
            #     pool.submit(self.get_page, q.get())
            pool.map(self.get_page, urls)


"""
    下面程序使用的是multiprocessing中的Pool进程池模块爬虫
"""


def put_url(url_queue, pagenum, base_url):
    for i in range(1, pagenum+1):
        url_queue.put(base_url.format(i))


def get_page(url_queue):
    while not url_queue.empty():
        ua = UserAgent(verify_ssl=False)
        headers = {
            'User-Agent': ua.random
        }
        url = url_queue.get()
        request = requests.get(url, headers=headers, verify=False)
        if request.status_code == 200:
            html = etree.HTML(request.text)
            contents = html.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
            for content in contents:
                item = dict()
                item['nickname'] = join_list(content.xpath('./div[1]/div/a/i/text()'))
                item['content'] = join_list(content.xpath('./p[@class="fonts"]/a/text()'))
                item['support'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
                item['not_support'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
                item['collect'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
                item['message'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
                item['share'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
                print(item)
        else:
            url_queue.put(url)


def join_list(res):
    return ''.join(res)


@timer
def main(threadnum, pagenum):

    base_url = 'https://www.xiaohua.com/duanzi?page={}'
    q = Manager().Queue()
    pool = Pool(threadnum)

    put_url(q, pagenum, base_url)
    for i in range(threadnum):
        pool.apply_async(get_page, args=(q,))

    pool.close()
    pool.join()


if __name__ == '__main__':

    threadNum = 3
    pagenum = 5
    # cra = Crawl(threadNum, pagenum)
    # cra.main()
    method = input('请输入使用类爬虫(class)还是函数爬虫(def): ')
    if method.strip() == 'class':
        cra = Crawl(threadNum, pagenum)
        cra.main()
    elif method.strip() == 'def':
        main(threadNum, pagenum)
    else:
        print('重新输入！')



