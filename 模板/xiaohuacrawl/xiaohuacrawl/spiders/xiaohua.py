# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from xiaohuacrawl.items import XiaohuacrawlItem


class XiaohuaSpider(CrawlSpider):
    name = 'xiaohua'
    # allowed_domains = ['xiaohua.com']
    start_urls = ['https://www.xiaohua.com/duanzi?page=1']

    rules = (
        Rule(LinkExtractor(allow=r'\/duanzi\?page=\d+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = XiaohuacrawlItem()
        if response.status == 200:
            contents = response.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
            for content in contents:
                item['nickname'] = self.join_list(content.xpath('./div[1]/div/a/i/text()').get())
                item['content'] = self.join_list(content.xpath('./p[@class="fonts"]/a/text()').get())
                item['support'] = int(self.join_list(content.xpath('./ul/li[1]/span/text()').get()))
                item['not_support'] = int(self.join_list(content.xpath('./ul/li[2]/span/text()').get()))
                item['collect'] = int(self.join_list(content.xpath('./ul/li[3]/span/text()').get()))
                item['message'] = int(self.join_list(content.xpath('./ul/li[4]/a/span/text()').get()))
                item['share'] = int(self.join_list(content.xpath('./ul/li[5]/span/text()').get()))
                print(item)
                yield item

    @staticmethod
    def join_list(res):
        return ''.join(res)