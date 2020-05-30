# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaohuaSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    nickname = scrapy.Field()
    content = scrapy.Field()
    support = scrapy.Field()
    not_support = scrapy.Field()
    collect = scrapy.Field()
    message = scrapy.Field()
    share = scrapy.Field()
