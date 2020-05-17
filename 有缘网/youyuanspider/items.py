# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YouyuanspiderItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    nick = scrapy.Field()
    addr = scrapy.Field()
    age = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    income = scrapy.Field()
    housing = scrapy.Field() #住房
    hoby = scrapy.Field()
    photo = scrapy.Field()
    soliloquy = scrapy.Field() # 独白
    native = scrapy.Field() # 籍贯
    education = scrapy.Field() # 学历
    child = scrapy.Field() #是否想要小孩
    heterosexual_type = scrapy.Field() # 异性类型
    live_parents = scrapy.Field() # 与父母同住
    marriage_status = scrapy.Field() # 婚姻状态
    work = scrapy.Field() # 职业
    long_distance = scrapy.Field() # 异地恋
    premarital_sex = scrapy.Field() #能否接受婚前性行为
    attractive_part = scrapy.Field() #最有魅力的部位
    boy_addr = scrapy.Field() #对方地址
    boy_height = scrapy.Field()
    boy_income = scrapy.Field()
    boy_age = scrapy.Field()
    boy_education = scrapy.Field()




