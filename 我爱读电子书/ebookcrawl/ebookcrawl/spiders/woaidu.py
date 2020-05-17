# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ebookcrawl.items import EbookcrawlItem


class WoaiduSpider(CrawlSpider):
    name = 'woaidu'
    allowed_domains = ['woaidu.org']
    start_urls = ['https://www.woaidu.org/']

    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 0.5,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': "UM_distinctid=16bcbe8a5ac24d-018f85bd0e81a-f353163-144000-16bcbe8a5ad7e8; look_logs_name[3]=%E6%B5%AA%E8%8D%A1%E7%9A%87%E5%B8%9D%E7%A7%98%E5%8F%B2; look_logs[3]=60421; look_logs_name[2]=%E6%97%A0%E9%99%90%E6%81%90%E6%80%96%E4%B9%8B%E9%9B%B7%E5%95%B8%E4%BC%A0%E5%A5%87; look_logs[2]=255999; __utmz=163097274.1562577654.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); look_logs_name[4]=%E9%99%8B%E9%A2%9C%E6%97%A0%E8%89%AF%E5%A6%83; look_logs[4]=39276; CNZZDATA1260857438=570081762-1562489578-%7C1562720436; __utma=163097274.1290480623.1562577654.1562648987.1562725037.4; __utmc=163097274; __utmt=1; __utmb=163097274.1.10.1562725037; wzws_cid=305480e6c16dfb16f3f3e11f5f2729d3c4fd99ede277e618939872eec3b2381a7665903ab2ab0eec5d902a682dfce4aefbc516e541f5241d25e4e8ee98eff2ac; PHPSESSID=5vko9h7cucmhped0s67btucf95; Hm_lvt_581659a3245cf1e8fbf04996a248077f=1562684309,1562720920,1562722729,1562725044; Hm_lpvt_581659a3245cf1e8fbf04996a248077f=1562725044",
            'Host': 'www.woaidu.org',
            'Pragma': 'no-cache',
            'Referer': 'https://www.woaidu.org/',
        }
    }

    rules = (
        Rule(LinkExtractor(allow=r'kehuan_s\d+.html')),
        Rule(LinkExtractor(allow=r'qita_s\d+.html')),
        Rule(LinkExtractor(allow=r'xuanhuan_s\d+.html')),
        Rule(LinkExtractor(allow=r'/book_\d+.html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        ebook = EbookcrawlItem()
        ebook_content = response.xpath('//div[@class="index-section"]')

        title = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/h1/text()').extract()
        author = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[2]/text()').extract()
        protagonist = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[4]/text()').extract()
        comment_count = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[5]/text()').extract()
        update_time = ebook_content.xpath('.//div[@class="commom-description fl"]/div[@class="des-right"]/p[6]/text()').extract()
        profile = ebook_content.xpath('.//div[@class="production producct-Message"]/p/text()').extract()
        download_url = ebook_content.xpath('.//div[@class="production producct-Message"]/ul[@class="dataList"]/li[1]/a[2]/@href').extract()

        if len(title) == 0:
            ebook['title'] = ''
        else:
            ebook['title'] = title[0]

        if len(author) == 0:
            ebook['author'] = ''
        else:
            ebook['author'] = author[0].strip()[3:]

        ebook['ebook_url'] = response.request.url

        if len(protagonist) == 0:
            ebook['protagonist'] = ''
        else:
            ebook['protagonist'] = protagonist[0].strip()[5:]

        if len(comment_count) == 0:
            ebook['comment_count'] = ''
        else:
            ebook['comment_count'] = comment_count[0].strip()[3:]

        if len(update_time) == 0:
            ebook['update_time'] = ''
        else:
            ebook['update_time'] = update_time[0].strip()[3:]

        if len(profile) == 0:
            ebook['profile'] = ''
        else:
            ebook['profile'] = profile[0]

        if len(download_url) == 0:
            ebook['download_url'] = ''
        else:
            ebook['download_url'] = download_url[0]

        print(ebook['title'], ebook['ebook_url'])
        yield ebook
