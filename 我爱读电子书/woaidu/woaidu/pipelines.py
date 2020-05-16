# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymysql

from scrapy.conf import settings


class WoaiduPipeline(object):

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
            """insert into ebook_table (classify,title,author,protagonist,ebook_url,comment_count,update_time,profile,about_url,download_url,latest_chapters,wonderful_chapters) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (item['classify'],
             item['title'],
             item['author'],
             item['protagonist'],
             item['ebook_url'],
             item['comment_count'],
             item['update_time'],
             item['profile'],
             item['about_url'],
             item['download_url'],
             item['latest_chapters'],
             item['wonderful_chapters']
             ))
        self.connect.commit()


        with open('ebook.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')


    def close_spider(self, spider):
        self.connect.close()
