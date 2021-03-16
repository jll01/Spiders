import requests
import time
import random
import pymysql
import queue

from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from lxml import etree


class HaoQiXin(object):
    def __init__(self):
        self.url = '''http://www.qdaily.com/articles/{}.html'''
        self.url_list = []
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()
        self.lock = Lock()
        self.pool = ThreadPoolExecutor(3)
        self.queue = queue.Queue()

    def put_url(self):
        for i in range(343, 65173):
            # self.url_list.append(self.url.format(i))
            self.queue.put(self.url.format(i))

    def get_source(self, url):
        # for url in self.url_list:
        headers = {'User-Agent': UserAgent().random}
        source = requests.get(url, headers=headers)
        if source.status_code == 200:
            html = etree.HTML(source.text)
            item = dict()
            try:
                item['url'] = url
                item['category'] = self.list2str(html.xpath('//div[@class="article-detail-hd"]/div[@class="category-title"]//span[2]/text()'))
                item['title'] = self.list2str(html.xpath('//div[@class="article-detail-hd"]/div[@class="category-title"]//h2[@class="title"]//text()'))
                item['name'] = self.list2str(html.xpath('//div[@class="article-detail-bd"]//div[@class="author"]/span[@class="name"]/text()'))
                item['avatar'] = self.list2str(html.xpath('//div[@class="article-detail-bd"]//div[@class="author"]/a/img/@src'))
                item['push_date'] = self.list2str(html.xpath('//div[@class="article-detail-bd"]//div[@class="author"]/span[contains(@class,"date")]/text()'))
                item['like'] = self.list2str(html.xpath('//div[@class="article-detail-bd"]//div[@class="com-share-favor"]//a[7]/span/@data-origincount'))
                # 摘录
                item['excerpt'] = self.list2str(html.xpath('//div[@class="article-detail-bd"]/p[@class="excerpt"]/text()'))
                item['content'] = self.list2str(html.xpath('//div[@class="article-detail-bd"]/div[@class="detail"]/p/text()'))

                print(item)
                self.save_content(item)
            except Exception as e:
                print('{}文章{}提取失败{}！'.format(url, item, e))

            time.sleep(random.uniform(0.8, 1.3))

    def save_content(self, item):
        self.lock.acquire()
        try:
            self.cur.execute(
                '''insert into haoqixin (url, category, title, name, avatar, push_date, like_num, excerpt, content) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (
                    item['url'],
                    item['category'],
                    item['title'],
                    item['name'],
                    item['avatar'],
                    item['push_date'],
                    item['like'],
                    item['excerpt'],
                    item['content']
                )
            )
            self.connect.commit()
        except Exception as e:
            print('数据{}出错{}'.format(item, e))
        self.lock.release()

    @staticmethod
    def list2str(inres):
        return ''.join(inres)

    def main(self):
        self.put_url()
        # self.get_source()
        while not self.queue.empty():
            self.pool.submit(self.get_source, self.queue.get())


if __name__ == '__main__':
    hq = HaoQiXin()
    hq.main()

