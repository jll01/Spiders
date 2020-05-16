# -*- coding: utf-8 -*-
import scrapy
import re
import requests
import urllib3

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from music.items import SingerItem, MusicDetail

urllib3.disable_warnings()

class Sp668Spider(CrawlSpider):
    name = 'sp668'
    allowed_domains = ['www.sq688.com']
    start_urls = ['http://www.sq688.com/']
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    }
    num = 1
    singer_id = []
    rules = (
        Rule(LinkExtractor(allow=r'/singer/\d+.html')),
        Rule(LinkExtractor(allow=r'/singer/\d+/\d+.html')),
        Rule(LinkExtractor(allow=r'detail/\d+.html'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'/download/\d+.html'), callback='download', follow=True),
    )

    def parse_item(self, response):
        singer = SingerItem()
        singer_desc = response.xpath('//div[@class="srt"]/div[@class="ww"]/div[@class="det"]')
        singer['classify'] = singer_desc.xpath('./p[1]/text()').get().strip()
        if singer['classify'] != '专辑合集':
            singer['name'] = singer_desc.xpath('./h2/text()').get().strip()
            singer['name_id'] = self.num
            self.singer_id.append({singer['name']:self.num})
            self.num += 1

            singer['addr'] = singer_desc.xpath('./p[2]/text()').get()
            singer['birthday'] = singer_desc.xpath('./p[3]/text()').get()
            singer['introduction'] = singer_desc.xpath('./p[5]/text()').get()
        else:
            singer['name'] = singer_desc.xpath('./p[2]/text()').get().strip()
            singer['name_id'] = self.num
            self.singer_id.append({singer['name']: self.num})
            self.num += 1

            singer['addr'] = singer_desc.xpath('./p[3]/text()').get()
            singer['birthday'] = singer_desc.xpath('./p[4]/text()').get()
            singer['introduction'] = singer_desc.xpath('./p[6]/text()').get()

        like_count = response.xpath('//div[@class="srt"]/div[@class="ww"]/div[@id="details"]/div[@class="good"]/a/span[@id="like"]/text()').get()
        if len(like_count) != 0:
            singer['like_count'] = int(like_count)
        else:
            singer['like_count'] = 0

        song_count = response.xpath('//div[@class="srt"]/div[@class="ww"]/div[@id="details"]/div[@class="good"]/a[2]/text()').get()
        if len(song_count) != 0:
            singer['song_count'] = int(song_count)
        else:
            singer['song_count'] = 0

        singer['home'] = response.request.url

        yield singer

        details = response.xpath('//div[@class="srt"]/div[@class="song"]/table[@class="songlist"]//tr')
        for detail in details[1:]:
            music = {}
            music['song'] = detail.xpath('./td[1]/a/text()').get()
            music['singer'] = detail.xpath('./td[2]/text()').get().strip()
            music['layout'] = detail.xpath('./td[3]/span/text()').get()
            music['size'] = detail.xpath('./td[4]/text()').get()
            heat = detail.xpath('./td[5]/text()').get()
            if len(heat) != 0:
                music['heat'] = int(heat)
            else:
                music['heat'] = 0
            music['date'] = detail.xpath('./td[6]/text()').get()
            for item_id in self.singer_id:
                for key,value in item_id.items():
                    # 合唱的按第一个歌手分类
                    if music['singer'].split('&')[0] == key:
                        music['singer_home'] = value

            down_url = 'https://www.sq688.com' + detail.xpath('./td[7]/a/@href').get()

            yield scrapy.Request(down_url, headers=self.headers, callback=self.download,meta={'values':music})

    def download(self,response):
        music = MusicDetail()
        res = response.meta['values']
        for key,value in res.items():
            music[key] = value

        url = response.xpath('//div[@class="url"]/p/text()').get()
        music['down_url'] = response.xpath('//div[@class="url"]/div[@class="ips"]/input/@value').get()
        pwd = re.findall(r'[密码|提取码][:|：]\s*?(\w{4})',url)
        if len(pwd) != 0:
            music['pwd'] = pwd[0]
        else:
            music['pwd'] = ''
        print(music['singer'],music['song'],music['date'],music['down_url'],music['pwd'])

        yield music



