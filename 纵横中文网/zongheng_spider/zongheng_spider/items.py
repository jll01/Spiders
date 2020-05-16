# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZonghengSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    spider_time = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    author_url = scrapy.Field()
    category = scrapy.Field()
    category_url = scrapy.Field()
    status = scrapy.Field()
    update_time = scrapy.Field()
    intro = scrapy.Field()
    book_update = scrapy.Field()
    update_url = scrapy.Field()
    number = scrapy.Field()
    all_recommend = scrapy.Field()
    click_num = scrapy.Field()
    week_recommend = scrapy.Field()
