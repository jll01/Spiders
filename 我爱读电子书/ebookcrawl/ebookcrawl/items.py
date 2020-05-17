# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EbookcrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ebook_url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    protagonist = scrapy.Field()
    comment_count = scrapy.Field()
    update_time = scrapy.Field()
    profile = scrapy.Field()
    download_url = scrapy.Field()
