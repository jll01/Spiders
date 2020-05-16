# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql

from music.items import SingerItem,MusicDetail
from scrapy.conf import settings


class MusicPipeline(object):

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
        if isinstance(item, SingerItem):
            self.cursor.execute(
                """insert into singer (name_id,name,classify,addr,birthday,introduction,like_count,song_count,home) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (item['name_id'],
                 item['name'],
                 item['classify'],
                 item['addr'],
                 item['birthday'],
                 item['introduction'],
                 item['like_count'],
                 item['song_count'],
                 item['home'],
                 ))
        elif isinstance(item, MusicDetail):
            self.cursor.execute(
                """insert into music (song,singer,layout,size,heat,date,down_url,pwd,foreign_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (item['song'],
                 item['singer'],
                 item['layout'],
                 item['size'],
                 item['heat'],
                 item['date'],
                 item['down_url'],
                 item['pwd'],
                 item['foreign_id'],
                 ))

        self.connect.commit()
        # with open('singer.json', 'a', encoding='utf-8') as f:
        #     f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')

    def close_spider(self, spider):
        self.connect.close()

