# -*- coding: utf-8 -*-
import scrapy

from xiaohua.items import XiaohuaItem
from fake_useragent import UserAgent


class DuanziSpider(scrapy.Spider):
    name = 'duanzi'
    allowed_domains = ['xiaohua.com']
    page = 1
    base_url = 'https://www.xiaohua.com/duanzi?page={}'
    start_urls = [base_url.format(page)]

    def parse(self, response):
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        item = XiaohuaItem()
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
                print(item)
                yield item

        if self.page < 5:
            self.page += 1
            yield scrapy.Request(self.base_url.format(self.page), headers=headers, callback=self.parse)

    def join_list(self, res):
        return ''.join(res)
