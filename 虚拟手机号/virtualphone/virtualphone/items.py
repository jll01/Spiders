# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VirtualphoneItem(scrapy.Item):
    # define the fields for your item here like:
    spidertime = scrapy.Field()
    virtualphone = scrapy.Field()
    fromphone = scrapy.Field()
    origin = scrapy.Field()
    content = scrapy.Field()
    getdate = scrapy.Field()
