# -*- coding: utf-8 -*-
import scrapy

from xiaohua_spider.items import XiaohuaSpiderItem
from fake_useragent import UserAgent
from scrapy_redis.spiders import RedisSpider


# class XiaohuaSpider(scrapy.Spider):
class XiaohuaSpider(RedisSpider):
    name = 'duanzi'
    redis_key = 'xiaohuaspider:start_urls'
    allowed_domains = ['xiaohua.com']
    page = 1
    base_url = 'https://www.xiaohua.com/duanzi?page={}'

    def parse(self, response):
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        item = XiaohuaSpiderItem()
        if response.status == 200:
            contents = response.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
            for content in contents:
                item['nickname'] = self.join_list(content.xpath('./div[1]/div/a/i/text()').extract())
                item['content'] = self.join_list(content.xpath('./p[@class="fonts"]/a/text()').extract())
                item['support'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()').extract()))
                item['not_support'] = int(self.join_list(content.xpath('./ul/li[2]/span/text()').extract()))
                item['collect'] = int(self.join_list(content.xpath('./ul/li[3]/span/text()').extract()))
                item['message'] = int(self.join_list(content.xpath('./ul/li[4]/a/span/text()').extract()))
                item['share'] = int(self.join_list(content.xpath('./ul/li[5]/span/text()').extract()))
                yield item

        if self.page < 1072:
            self.page += 1
            url = self.base_url.format(self.page)
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    @staticmethod
    def join_list(res):
        return ''.join(res)
