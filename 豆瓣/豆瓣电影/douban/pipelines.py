# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.conf import settings
import json



class DoubanPipeline(object):

    def __init__(self):
        # self.filename = open('douban.json', 'w', encoding='utf-8')
        self.connect = pymysql.connect(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DBNAME'],
            port = int(settings['MYSQL_PORT']),
            # charset='utf8',
            # use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        # try:
        self.cursor.execute(
            "insert into doubantable(id,title,bd,star,quote) values(%s,%s, %s, %s, %s)",
            (int(item['id']),
             item['title'],
             item['bd'],
             item['star'],
             item['quote']
             ))
        self.connect.commit()

        return item


    def close_spider(self, spider):
    #     self.filename.close()
        self.connect.close()

