# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymysql

from scrapy.conf import settings


class DongguanPipeline(object):

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DBNAME'],
            port=int(settings['MYSQL_PORT']),
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):

        self.cursor.execute(
            "insert into dongguantable(number_title,name_title,time_title,title,content,parsetype,url) values(%s,%s,%s,%s,%s,%s,%s)",
            (
                item['number_title'],
                item['name_title'],
                item['time_title'],
                item['title'],
                item['content'],
                item['parsetype'],
                item['url'],
             ))
        self.connect.commit()

        with open('sun.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')

        return item

    def close_spider(self, spider):
        self.connect.close()
