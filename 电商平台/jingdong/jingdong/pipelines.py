# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
from scrapy.conf import settings


class JingdongPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host = settings['MYSQL_HOST'],
            port = settings['MYSQL_PORT'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWD'],
            db = settings['MYSQL_DB'],
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        self.cursor.execute(
            """insert into jd (date,url,shop_name,goods,brand,price,comment_count,good_rate,poor_rate,weight,category,sugar,fat,addr,select_shop,image) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['date'],
                item['url'],
                item['shop_name'],
                item['goods'],
                item['brand'],
                item['price'],
                item['comment_count'],
                item['good_rate'],
                item['poor_rate'],
                item['weight'],
                item['category'],
                item['sugar'],
                item['fat'],
                item['addr'],
                item['select_shop'],
                item['image'],
            ))
        self.connect.commit()

        with open('jd.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')

    def close_spider(self, spider):
        self.connect.close()

