# -*- coding: utf-8 -*-
import scrapy
import time

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from youyuanspider.items import YouyuanspiderItem

class YouyuanSpider(CrawlSpider):
    # time.sleep(3600)
    name = 'youyuan'
    allowed_domains = ['www.youyuan.com']
    start_urls = [
        'http://www.youyuan.com/find/beijing/mm18-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/shanghai/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/tianjin/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/chongqing/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/anhui/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/hunan/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/hubei/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/jiangsu/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/zhejiang/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/sichuan/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/guizhou/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/gansu/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/qinghai/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/shanxi/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/shandong/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/sx/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/henan/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/heilongjiang/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/hebei/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/fujian/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/yunnan/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/jiangxi/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/guangdong/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/liaoning/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/jilin/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/neimeng/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/guangxi/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/xinjiang/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/xizang/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/ningxia/mm0-0/advance-0-0-0-0-0-0-0/p1/',
        'http://www.youyuan.com/find/hainan/mm0-0/advance-0-0-0-0-0-0-0/p1/',
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/find/.*?/mm0-0/advance-0-0-0-0-0-0-0/p\d+/')),
        Rule(LinkExtractor(allow=r'/\d+-profile/'), callback='parse_item',follow=True),
    )

    def parse_item(self, response):
        item = YouyuanspiderItem()
        item['url'] = response.request.url
        item['nick'] = response.xpath('//dl[@class="personal_cen"]/dd/div[@class="main"]/strong/text()').get()
        info = response.xpath('//dl[@class="personal_cen"]/dd/p/text()').get().split()
        item['addr'] = info[0]
        item['age'] = info[1]
        item['height'] = info[2]
        item['income'] = info[3]
        item['housing'] = info[4]
        item['hoby'] = self.get_hoby(response)
        item['photo'] = self.get_photo(response)
        item['soliloquy'] = response.xpath('//div[@class="pre_data"]/ul[@class="requre"]/li[1]/p/text()').get().strip()

        details = self.get_details(response)
        item['native'] = details['native']
        item['weight'] = details['weight']
        item['education'] = details['education']
        item['child'] = details['child']
        item['heterosexual_type'] = details['heterosexual_type']
        item['live_parents'] = details['live_parents']
        item['marriage_status'] = details['marriage_status']
        item['work'] = details['work']
        item['long_distance'] = details['long_distance']
        item['premarital_sex'] = details['premarital_sex']
        item['attractive_part'] = details['attractive_part']

        boys = self.get_boys_info(response)
        item['boy_addr'] = boys['boy_addr']
        item['boy_height'] = boys['boy_height']
        item['boy_income'] = boys['boy_income']

        item['boy_age'] = boys['boy_age']
        item['boy_education'] = boys['boy_education']

        print((item['nick'],item['addr'],item['age']))

        yield item

    def get_hoby(self,response):
        hobies = response.xpath('//dl[@class="personal_cen"]/dd/ol[@class="hoby"]/li')
        res_hoby = []
        for hoby in hobies:
            res_hoby.append(hoby.xpath('./text()').get().strip())

        return '|'.join(res_hoby)

    def get_photo(self,response):
        phtotes = response.xpath('//div[@id="photo"]//ul[@class="block_photo"]/li//a/img/@src')
        res_photo = []
        for photo in phtotes:
            res_photo.append(photo.get().strip())

        return '|'.join(res_photo)

    def get_details(self,response):
        details_1 = response.xpath('//div[@class="pre_data"]/ul[@class="requre"]/li[2]/div[@class="message"]/ol[1]')
        details_2 = response.xpath('//div[@class="pre_data"]/ul[@class="requre"]/li[2]/div[@class="message"]/ol[2]')
        res_detail = {}
        for detail_1 in details_1:
            res_detail['native'] = detail_1.xpath('./li[1]/span/text()').get().strip()
            res_detail['weight'] = detail_1.xpath('./li[2]/span/text()').get().strip()
            res_detail['education'] = detail_1.xpath('./li[3]/span/text()').get().strip()
            res_detail['child'] = detail_1.xpath('./li[5]/span/text()').get().strip()
            res_detail['heterosexual_type'] = detail_1.xpath('./li[6]/span/text()').get().strip()
            res_detail['live_parents'] = detail_1.xpath('./li[7]/span/text()').get().strip()

        for detail_2 in details_2:
            res_detail['marriage_status'] = detail_2.xpath('./li[1]/span/text()').get().strip()
            res_detail['work'] = detail_2.xpath('./li[3]/span/text()').get().strip()
            res_detail['long_distance'] = detail_2.xpath('./li[5]/span/text()').get().strip()
            res_detail['premarital_sex'] = detail_2.xpath('./li[6]/span/text()').get().strip()
            res_detail['attractive_part'] = detail_2.xpath('./li[7]/span/text()').get().strip()

        return res_detail

    def get_boys_info(self,response):
        boys_1 = response.xpath('//div[@class="pre_data"]/ul[@class="requre"]/li[3]/div[@class="message"]/ol[1]')
        boys_2 = response.xpath('//div[@class="pre_data"]/ul[@class="requre"]/li[3]/div[@class="message"]/ol[2]')

        boys = {}
        for boy_1 in boys_1:
            boys['boy_addr'] = boy_1.xpath('./li[1]/span/text()').get().replace(' ','')
            boys['boy_height'] = boy_1.xpath('./li[2]/span/text()').get().replace(' ','')
            boys['boy_income'] = boy_1.xpath('./li[3]/span/text()').get().replace(' ','')

        for boy_2 in boys_2:
            boys['boy_age'] = boy_2.xpath('./li[1]/span/text()').get().replace(' ','')
            boys['boy_education'] = boy_2.xpath('./li[2]/span/text()').get().replace(' ','')

        return boys



