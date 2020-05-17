# -*- coding: utf-8 -*-
import scrapy
import re
import math
import time

from virtualphone.items import VirtualphoneItem


class VirtualSpider(scrapy.Spider):
    name = 'virtual'
    allowed_domains = ['www.pdflibr.com']
    url = 'https://www.pdflibr.com/?page={}'
    page = 1
    saveurls = []
    content_page = 1

    def start_requests(self):
        while self.page <= 10:
            yield scrapy.Request(self.url.format(self.page), callback=self.parse)
            self.page += 1

    def parse(self, response):
        urls = response.xpath('//div[@class="container-fluid"]/div[contains(@class,"sms-number-list")]/div[contains(@class,"sms-number-read")]/a/@href')
        phones = response.xpath('//div[@class="container-fluid"]/div[contains(@class,"sms-number-list")]/div[contains(@class,"number-list-flag")]/h3/text()')
        counts = response.xpath('//div[@class="container-fluid"]/div[contains(@class,"sms-number-list")]/div[contains(@class,"number-list-info")]/p/b/text()')
        for content in zip(phones,urls,counts):
            if content[1].extract() not in self.saveurls:
                url = 'https://www.pdflibr.com' + content[1].extract()
                phone = content[0].extract()
                count = int(content[2].extract())
                self.saveurls.append(content[1].extract())
                while self.content_page <= math.ceil(count/10):
                    yield scrapy.Request(url + '?page={}'.format(self.content_page),callback=self.parse_item,meta={'phone':phone})
                    self.content_page += 1

    def parse_item(self, response):
            item = VirtualphoneItem()
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['virtualphone'] = response.meta['phone']
            item['fromphone'] = response.xpath('//section[@class="container-fluid sms_content"]/div[@class="container sms-content-list"]/div[@class="sms-content-table table-responsive"]/table[@class="table table-hover"]/tbody/tr[1]/td[2]/text()').get()
            if len(item['fromphone']) != 0:
                item['content'] = response.xpath('//section[@class="container-fluid sms_content"]/div[@class="container sms-content-list"]/div[@class="sms-content-table table-responsive"]/table[@class="table table-hover"]/tbody/tr[1]/td[3]/text()').get()
                item['origin'] = self.get_fromcontent(item['content'])
                item['getdate'] = response.xpath('//section[@class="container-fluid sms_content"]/div[@class="container sms-content-list"]/div[@class="sms-content-table table-responsive"]/table[@class="table table-hover"]/tbody/tr[1]/td[4]/time/text()').get()

                print(item)
                yield item

    def get_fromcontent(self, res):
        try:
            return re.findall(r'【(.*?)】', res)[0]
        except Exception as e:
            try:
                return re.findall(r'\[(.*?)\]', res)[0]
            except Exception as e:
                return '未知来源'
