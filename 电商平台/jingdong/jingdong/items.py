# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JingdongItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    shop_name = scrapy.Field()
    goods = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    comment_count = scrapy.Field()
    good_rate = scrapy.Field()
    poor_rate = scrapy.Field()
    select_shop = scrapy.Field()
    image = scrapy.Field()
    weight = scrapy.Field()
    category = scrapy.Field()
    sugar = scrapy.Field()
    fat = scrapy.Field()
    addr = scrapy.Field()
