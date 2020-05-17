# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SingerItem(scrapy.Item):
    # define the fields for your item here like:
    name_id = scrapy.Field()
    name = scrapy.Field()
    classify = scrapy.Field()
    addr = scrapy.Field()
    birthday = scrapy.Field()
    introduction = scrapy.Field()
    like_count = scrapy.Field()
    song_count = scrapy.Field()
    home = scrapy.Field()


class MusicDetail(scrapy.Item):
    song = scrapy.Field()
    singer = scrapy.Field()
    layout = scrapy.Field()  # 类型
    size = scrapy.Field()
    heat = scrapy.Field()
    date = scrapy.Field()
    down_url = scrapy.Field()
    pwd = scrapy.Field()
    foreign_id = scrapy.Field()



