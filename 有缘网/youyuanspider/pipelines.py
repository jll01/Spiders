# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
import time

from redis import StrictRedis
from scrapy.conf import settings

class YouyuanspiderPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DBNAME'],
            port=int(settings['MYSQL_PORT']),
        )
        self.cursor = self.connect.cursor()

        self.redis = StrictRedis(
            host=settings['REDIS_HOST'],
            port=settings['REDIS_PORT'],
            db=settings['REDIS_DB'],
        )

    def process_item(self, item, spider):
        self.cursor.execute(
            """insert into youyuan_all (nick,addr,age,height,income,housing,hoby,photo,soliloquy,native,weight,education,child,heterosexual_type,live_parents,marriage_status,work,long_distance,premarital_sex,attractive_part,boy_addr,boy_height,boy_income,boy_age,boy_education,url) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (item['nick'],
             item['addr'],
             item['age'],
             item['height'],
             item['income'],
             item['housing'],
             item['hoby'],
             item['photo'],
             item['soliloquy'],
             item['native'],
             item['weight'],
             item['education'],
             item['child'],
             item['heterosexual_type'],
             item['live_parents'],
             item['marriage_status'],
             item['work'],
             item['long_distance'],
             item['premarital_sex'],
             item['attractive_part'],
             item['boy_addr'],
             item['boy_height'],
             item['boy_income'],
             item['boy_age'],
             item['boy_education'],
             item['url'],
             ))
        self.connect.commit()

        now = int(time.time()*1000)
        self.redis.hmset(now, item)

    def close_spider(self, spider):
        self.connect.close()