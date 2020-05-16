# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dongguan.items import DongguanItem

class SunSpider(CrawlSpider):
    name = 'sun'
    allowed_domains = ['wz.sun0769.com']
    start_urls = ['http://wz.sun0769.com/index.php/question/questionType?type=4&page=0']
    rules = (
        Rule(LinkExtractor(allow=r'type=4&page=\d+')),
        Rule(LinkExtractor(allow=r'show?id=\d+'), callback="parse_item", follow=False),
        Rule(LinkExtractor(allow=r'question/\d+/\d+.shtml'), callback="parse_item"),
    )

    def parse_item(self, response):
        item = DongguanItem()


        # 编号：
        item['number_title'] = response.xpath('//div[@class="wzy1"]//td/span[2]/text()').extract()[0].split('：')[-1].split(':')[-1]
        
        other = response.xpath('//div[@class="wzy3_2"]/span/text()').extract()[0]
        # 网友： 
        item['name_title'] = other.split()[0].split('：')[-1]
        # 时间:
        item['time_title'] = other.split()[1].split('：')[-1] +' ' +  other.split()[-1]

        # 标题
        item['title'] = response.xpath('//div[@class="wzy1"]//td/span[1]/text()').extract()[0].split('：')[-1]

        # 内容(无图片):
        # content = response.xpath('//div[@class="wzy1"]//tr/td[@class="txt16_3"]/text()').extract()[0]
        # 内容(有图片)：
        content_has = response.xpath('//div[@class="wzy1"]//td/div[@class="contentext"]/text()').extract()
        content_no = response.xpath('//div[@class="wzy1"]//tr/td[@class="txt16_3"]/text()').extract()
        string_content = ''

        if len(content_has) == 0:
            for i in content_no:
                string_content += i.strip()
            item['content'] = string_content
        else:
            for i in content_has:
                string_content += i.strip()
            item['content'] = string_content

        # 处理状态：
        item['parsetype'] = response.xpath('//div[@class="wzy3_1"]/span/text()').extract()[0]   
        item['url'] = response.url

        yield item
