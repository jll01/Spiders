# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HaozhiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    course_url = scrapy.Field()
    title = scrapy.Field()
    course_img = scrapy.Field()
    # 评价数
    appraise = scrapy.Field()
    # 星星
    stars = scrapy.Field()
    # 课时
    class_hour = scrapy.Field()
    # 学员
    student_num = scrapy.Field()
    # 浏览
    scan = scrapy.Field()
    # 课程教师
    course_teacher = scrapy.Field()
    # 老师主页
    teacher_url = scrapy.Field()
    # 课程数
    course_num = scrapy.Field()
    # 粉丝
    fans = scrapy.Field()
