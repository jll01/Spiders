# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.spiders import CrawlSpider
from scrapy_redis.spiders import RedisCrawlSpider
from xiaohua_spider_redis.items import XiaohuaSpiderRedisItem


# class XiaohuaSpider(CrawlSpider):
class XiaohuaSpider(RedisCrawlSpider):
    name = 'xiaohua'
    allowed_domains = ['xiaohua.com']
    # start_urls = ['https://www.xiaohua.com/duanzi?page=1']
    redis_key = 'xiaohuaspider:start_urls'
    rules = (
        Rule(LinkExtractor(allow=r'page=\d+'), callback='parse_item', follow=True),
    )

    # 动态域获取, 使用allowed_domains或者自定义
    # def __init__(self, *args, **kwargs):
    #     # Dynamically define the allowed domains list.
    #     domain = kwargs.pop('domain', '')
    #     self.allowed_domains = filter(None, domain.split(','))
    #     super(XiaohuaSpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):

        item = XiaohuaSpiderRedisItem()
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

    @staticmethod
    def join_list(res):
        return ''.join(res)
