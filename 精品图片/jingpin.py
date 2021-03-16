import re
import os
import asyncio
import aiohttp

from fake_useragent import UserAgent
from lxml import etree


class JingPin(object):
    def __init__(self):
        self.ua = UserAgent()
        self.offset = 1
        self.base_url = 'http://www.qqzhpt.com/meitu/page/{}/'
        self.urls = []
        self.sem = asyncio.Semaphore(10)

    def put_urls(self):
        while self.offset <= 738:
            self.urls.append(self.base_url.format(self.offset))
            self.offset += 1

    async def get_image_url(self, url):
        async with self.sem:
            async with aiohttp.ClientSession() as session:
                async with await session.get(url, headers={'User-Agent': self.ua.random}) as response:
                    html = etree.HTML(await response.read())
                    urls = html.xpath('//div[@class="lsit-items"]/div[@class="data-list"]/a/@href')
                    titles = html.xpath('//div[@class="lsit-items"]/div[@class="data-list"]/a/@title')
                    for title, url in zip(titles, urls):
                        await self.image_detail(title, url, session)

    async def image_detail(self, title, url, session):
        page = 1
        while True:
            page_url = url + '/' + str(page)
            async with await session.get(page_url, headers={'User-Agent': self.ua.random}) as response_detail:
                html_detail = etree.HTML(await response_detail.read())
                image_urls = html_detail.xpath('//div[@id="imgs-list"]/img/@src')
                if len(image_urls) != 0:
                    for image_url in image_urls:
                        await self.download_image(title, image_url, session)
                    page += 1
                else:
                    break

    async def download_image(self, title, url, session):
        file = os.path.join(os.getcwd(), 'images', title)
        if not os.path.exists(file):
            os.mkdir(file)
        print('正在下载{}'.format(url))
        async with await session.get(url, headers={'User-Agent': self.ua.random}) as response_image:
            name = ''.join(re.findall(r'(\d+.jpg)', url))
            with open('{}/{}'.format(file, name), 'wb') as f:
                f.write(await response_image.read())
        print('下载完成{}'.format(url))

    def main(self):
        self.put_urls()

        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self.get_image_url(url)) for url in self.urls]

        loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    jp = JingPin()
    jp.main()
