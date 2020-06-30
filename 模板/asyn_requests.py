#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   asyn_requests.py
# @Time    :   2020/6/9 11:13
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import asyncio
import aiohttp
import time
import urllib3

from lxml import etree
from fake_useragent import UserAgent


# 计时装饰器
def timer(inner):
    def func(self, *args, **kwargs):
        start = time.time()
        inner(self, *args, **kwargs)
        print("complete in {} seconds".format(time.time() - start))

    return func


class Crawl(object):
    """
        异步爬虫
    """
    def __init__(self, page_number, th_num):
        # 爬取的页码
        self.page_number = page_number
        # 起始url
        self.base_url = 'https://www.xiaohua.com/duanzi?page={}'
        # 使用UserAgent().random自己生成User-Agent
        self.ua = UserAgent(verify_ssl=False)
        # 队列
        self.queue = asyncio.Queue()
        # 存储url
        self.urls = []
        # 控制并发量
        self.sem = asyncio.Semaphore(th_num)

    async def put_url(self):
        # 将要爬取的url加入到队列或者urls列表中
        for i in range(1, self.page_number + 1):
            await self.queue.put(self.base_url.format(i))
            # self.urls.append(self.base_url.format(i))

    async def send_requests(self):
        # 发送请求
        # 队列
        while not self.queue.empty():
            await self.page_response(await self.queue.get())
        # 列表
        # await asyncio.wait([self.page_response(url) for url in self.urls])

    async def page_response(self, url):
        # 获取页面响应
        # 生成headers
        headers = {
            'User-Agent': self.ua.random
        }
        async with self.sem:
            # 和requests.session()相似
            async with aiohttp.ClientSession() as session:
                async with await session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        # 获取页面成功的时候调用get_page()提取页面信息
                        await self.get_page(await resp.read())
                    else:
                        # 请求失败将当前url重新加入到队列，等待重新请求
                        await self.queue.put(url)

    async def get_page(self, response):
        # 提取页面信息
        html = etree.HTML(response)
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
        # xpath提取的信息是列表，有些提取为空列表，避免下标提取报错，使用join()
        return ''.join(res)

    @timer
    def main(self):
        loop = asyncio.get_event_loop()

        # 异步任务
        # tasks = [
        #     asyncio.ensure_future(self.put_url()),
        #     asyncio.ensure_future(self.send_requests())
        # ]
        tasks = [
            loop.create_task(self.put_url()),
            loop.create_task(self.send_requests())
        ]
        loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    urllib3.disable_warnings()
    # 并发量
    thnum = 5
    pagenumber = 10
    cra = Crawl(pagenumber, thnum)
    cra.main()
