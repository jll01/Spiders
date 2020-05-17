# -*- coding: utf-8 -*-
import scrapy
from mySpiser.items import MyspiserItem

class ItcastSpider(scrapy.Spider):
	name = 'itcast'
	allowed_domains = ['http://www.itcast.cn']
	start_urls = ['http://www.itcast.cn/channel/teacher.shtml#']


	def parse(self, response):
		# with open('teacher.html', 'wb') as f:
		# 	f.write(response.body)
		# teacher = []
		teacher_list = response.xpath('//div[@class="li_txt"]')
		for each in teacher_list:
			item = MyspiserItem()
			name = each.xpath('./h3/text()').extract()
			title = each.xpath('./h4/text()').extract()
			info = each.xpath('./p/text()').extract()

			item['name'] = name[0]
			item['title'] = title[0]
			item['info'] = info[0]
			# print(name[0], title[0], info[0])
			yield item
			# teacher.append(item)
		# return teacher
