# -*- coding: utf-8 -*-
import scrapy
import re
import os
import time
import random
import chardet


class BianSpider(scrapy.Spider):
    name = 'bian'
    allowed_domains = ['pic.netbian.com']
    page = 1
    url = 'http://pic.netbian.com/index{}.html'
    start_urls = [url.format('')]
    file_path = os.path.join(os.path.abspath(os.path.dirname(os.getcwd())), 'images')
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    def parse(self, response):
        if response.status == 200:
            # encode_str = chardet.detect(response.body)
            contents = re.findall(r'<li><a.*?><img\s+src=\"(.*?)\"\s+alt=\"(.*?)\".*?</b></a></li>', response.body.decode('gbk'))
            url_str = 'http://pic.netbian.com'
            for content in contents:
                url = url_str + content[0]
                title = content[1]
                print(url, title)
                yield scrapy.Request(url, callback=self.save, meta={'title': title})

            self.page += 1
            time.sleep(random.uniform(2, 4))
            yield scrapy.Request(self.url.format('_' + str(self.page)), callback=self.parse)

    def save(self, response):
        item = {}
        title = response.meta['title']
        item['title'] = re.sub(r'[: \ / * ? < > | " ]', '', title)
        item['file_path'] = os.path.join(self.file_path, title + '.jpg')
        item['url'] = response.url
        item['image'] = response.body

        yield item
