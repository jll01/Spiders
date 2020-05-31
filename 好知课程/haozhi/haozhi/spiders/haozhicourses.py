# -*- coding: utf-8 -*-
import scrapy
import re

from haozhi.items import HaozhiItem
from fake_useragent import UserAgent


class HaozhicoursesSpider(scrapy.Spider):
    name = 'haozhicourses'
    # allowed_domains = ['haozhi.com']
    pagenum = 1
    base_url = 'http://www.howzhi.com/courses?page={}'
    start_urls = [base_url.format(pagenum)]
    course_url = 'http://www.howzhi.com{}'

    def parse(self, response):
        while True:
            headers = {'User-Agent': UserAgent().random}
            course_urls = response.xpath('//div[@class="col-md-9"]//div[contains(@class, "course-item")]/div[@class="course-img"]/a/@href').extract()
            for url in course_urls:
                url = self.course_url.format(url)
                yield scrapy.Request(url, headers=headers, callback=self.get_page)

            if self.pagenum <= 203:
                self.pagenum += 1
                yield scrapy.Request(self.base_url.format(self.pagenum), headers=headers, callback=self.parse)
            else:
                break

    def get_page(self, response):
        item = HaozhiItem()
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



