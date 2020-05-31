# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from haozhi_crawlspider.items import HaozhiCrawlspiderItem


class HaozhiSpider(CrawlSpider):
    name = 'haozhi'
    # allowed_domains = ['haozhi.com']
    start_urls = ['http://www.howzhi.com/courses']
    course_url = 'http://www.howzhi.com{}'

    rules = (
        Rule(LinkExtractor(allow=r'\/courses\?page=\d+')),
        Rule(LinkExtractor(allow=r'/course/\d+/'), callback='parse_item', follow=False)
    )

    def parse_item(self, response):
        item = HaozhiCrawlspiderItem()
        item['course_url'] = response.url
        item['course_img'] = self.join_str(response.xpath('//div[@class="container"]//div[contains(@class, "pic")]/img/@src').extract())
        item['title'] = self.join_str(response.xpath('//div[@class="container"]//div[contains(@class, "info")]/h1/text()').extract())
        item['appraise'] = self.get_num(self.join_str(response.xpath('//div[@class="container"]//div[contains(@class, "info")]/div[@class="score"]/text()').extract()))
        item['stars'] = self.join_num(response.xpath('//div[@class="container"]//div[contains(@class, "info")]/div[@class="score"]/span[2]/text()').extract())
        item['class_hour'] = self.get_num(self.join_str(response.xpath('//div[@class="container"]//div[contains(@class, "info")]/ul[contains(@class, "metas")]/li[1]/p/text()').extract()))
        item['student_num'] = self.get_num(self.join_str(response.xpath('//div[@class="container"]//div[contains(@class, "info")]/ul[contains(@class, "metas")]/li[2]/p/text()').extract()))
        item['scan'] = self.get_num(self.join_str(response.xpath('//div[@class="container"]//div[contains(@class, "info")]/ul[contains(@class, "metas")]/li[3]/p/text()').extract()))
        item['course_teacher'] = self.join_str(response.xpath('//section[@class="container"]/div[@class="row"]//div[contains(@class, "teach-info")]/p[@class="text-o-show"]/a/text()').extract())
        item['teacher_url'] = self.course_url.format(self.join_str(response.xpath('//section[@class="container"]/div[@class="row"]//div[contains(@class, "teach-info")]/p[@class="text-o-show"]/a/@href').extract()))
        item['course_num'] = self.join_num(response.xpath('//section[@class="container"]/div[@class="row"]//div[contains(@class, "teach-info")]/p[2]/a[1]/span/text()').extract())
        item['fans'] = self.join_num(response.xpath('//section[@class="container"]/div[@class="row"]//div[contains(@class, "teach-info")]/p[2]/a[2]/span/text()').extract())
        print(item)
        yield item

    @staticmethod
    def join_str(in_list):
        return ''.join(in_list).strip()

    @staticmethod
    def join_num(in2num):
        try:
            res = int(''.join(in2num).strip())
        except Exception as e:
            res = 0
        return res

    @staticmethod
    def get_num(in_str):
        try:
            res = int(''.join(re.findall(r'(\d+)', in_str)))
        except Exception as e:
            res = 0

        return res
