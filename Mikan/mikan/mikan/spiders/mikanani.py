# -*- coding: utf-8 -*-
import scrapy
import random
import time
import redis

from fake_useragent import UserAgent
from scrapy_redis.spiders import RedisSpider
from mikan.items import MikanItem


# class MikananiSpider(scrapy.Spider):
class MikananiSpider(RedisSpider):
    name = 'mikanani'
    allowed_domains = ['mikanani.me']
    # start_urls = ['http://mikanani.me/']
    redis_key = 'mikan:start_urls'
    base_url = 'https://mikanani.me/Home/Classic/{}'
    page_num = 1
    add_url = '''https://mikanani.me/{}'''
    # pool = redis.ConnectionPool(host='192.168.1.102', port=6379, db=6)
    # red = redis.Redis(connection_pool=pool)

    def parse(self, response):
        while True:
            headers = {
                'User-Agent': UserAgent(verify_ssl=False).random
            }
            try:
                all_contents = response.xpath('//div[@id="sk-body"]/table/tbody/tr')
                if not all_contents:
                    raise Exception('该请求网址下所有页码获取完成！')
            except Exception as e:
                print(e)
                break
            else:
                for all_content in all_contents:
                    item = MikanItem()

                    item['update_time'] = self.join2str(all_content.xpath('./td[1]/text()').extract())
                    item['fansub_group'] = self.join2str(all_content.xpath('./td[2]//text()').extract())
                    item['fanzu_url'] = self.add_url.format(self.join2str(all_content.xpath('./td[3]/a[1]/@href').extract()))
                    item['fanzu_name'] = self.join2str(all_content.xpath('./td[3]/a[1]/text()').extract())
                    item['magnet'] = self.join2str(all_content.xpath('./td[3]/a[2]/@data-clipboard-text').extract())
                    item['size'] = self.join2str(all_content.xpath('./td[4]/text()').extract())
                    item['download'] = self.add_url.format(self.join2str(all_content.xpath('./td[5]/a/@href').extract()))

                    yield item
                    # self.save2redis(item)
                self.page_num += 1
                time.sleep(random.uniform(1, 1.5))
                url = self.base_url.format(self.page_num)
                yield scrapy.Request(url, headers=headers, callback=self.parse)

    @staticmethod
    def join2str(inner):
        return ''.join(inner).replace('\r\n', '').strip()

    # def save2redis(self, item):
    #     self.red.hmset(int(time.time() * 1000), item)
