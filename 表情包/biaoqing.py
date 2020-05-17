#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   biaoqing.py
# @Time    :   2020/3/13 21:09:13
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import re
import os
import asyncio
import aiohttp
import random

from fake_useragent import UserAgent
from lxml import etree


class BiaoQing(object):
    def __init__(self):
        self.base_url = 'https://fabiaoqing.com/bqb/lists/type/hot//bqb/lists/type/hot/page/{}.html'
        self.offset = 1
        self.ua = UserAgent()
        self.urls = []
        self.sem = asyncio.Semaphore(5)

    def put_urls(self):
        while self.offset <= 1008:
            self.urls.append(self.base_url.format(self.offset))
            self.offset += 1

    async def get_urls(self, url):
        async with self.sem:
            async with aiohttp.ClientSession() as session:
                async with await session.get(url, headers={'User-Agent': self.ua.random}) as response:
                    html = etree.HTML(await response.read())
                    urls = html.xpath('//div[@id="container"]//div[@id="bqblist"]/a/@href')
                    titles = html.xpath('//div[@id="container"]//div[@id="bqblist"]/a/@title')
                    for title, url in zip(titles, urls):
                        await self.get_bqb_urls(title, url, session)
                        await asyncio.sleep(random.uniform(0.5, 1))

    async def get_bqb_urls(self, filename, url, session):
        file = os.path.join(os.getcwd(), 'images', filename.replace('/', '-'))
        if not os.path.exists(file):
            os.mkdir(file)
        async with await session.get('https://fabiaoqing.com' + url, headers={'User-Agent': self.ua.random}) as response_bqb:
            text_res = await response_bqb.text()
            title_urls = re.findall(r'<img\s+class="bqbppdetail\s+lazy"\s+data-original="(.*?)"\s+title="(.*?)"\s+alt=".*?"\s+style=".*?"/>\s+', text_res)
            for title_url in title_urls:
                await self.download(title_url[0], title_url[1], file, session)
                await asyncio.sleep(random.uniform(0.5, 1))

    async def download(self, url, name, file, session):
        print('开始下载{}'.format(url))
        async with await session.get(url, headers={'User-Agent': self.ua.random}) as down_bqb:
            try:

                with open('{}/{}.{}'.format(file, name, url[-3:]), 'wb') as f:
                    f.write(await down_bqb.read())
            except Exception as err:
                print(err)
        print('下载完成{}'.format(url))

    def main(self):
        self.put_urls()
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self.get_urls(url)) for url in self.urls]
        loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    bq = BiaoQing()
    bq.main()
