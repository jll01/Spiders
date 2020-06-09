# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MikanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    update_time = scrapy.Field()
    fansub_group = scrapy.Field()
    fanzu_url = scrapy.Field()
    fanzu_name = scrapy.Field()
    magnet = scrapy.Field()
    size = scrapy.Field()
    download = scrapy.Field()
