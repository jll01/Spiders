# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem


class DoubanmovieSpider(scrapy.Spider):
    name = 'doubanmovie'
    allowed_domains = ['movie.douban.com']
    url = 'https://movie.douban.com/top250?start='
    offset = 0
    start_urls = [url + str(offset)]
    num = 1

    def parse(self, response):
        item = DoubanItem()
        movies = response.xpath('//div[@class="info"]')
        for each in movies:
            item['id'] = self.num
            item['title'] = each.xpath('.//span[@class="title"][1]/text()').extract()[0]
            bd = each.xpath('.//div[@class="bd"]/p/text()').extract()
            item['bd'] = ''.join(bd).strip().replace('\xa0', '').replace(' ', '').replace('\n', '')
            item['star'] = each.xpath('.//div[@class="star"]/span[@class="rating_num"]/text()').extract()[0]
            item['quote'] = each.xpath('.//p[@class="quote"]/span/text()').extract()[0]
            self.num += 1
            yield item

        if self.offset < 225:
            self.offset += 25
            yield scrapy.Request(self.url+str(self.offset), callback=self.parse)