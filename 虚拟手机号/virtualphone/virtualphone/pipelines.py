# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql


class VirtualphonePipeline(object):

    def __init__(self):
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def process_item(self, item, spider):
        self.cur.execute(
            """insert into virtualphone (spidertime,virtualphone,fromphone,origin,getdate,content) values (%s,%s,%s,%s,%s,%s)""",
            (
                item['spidertime'],
                item['virtualphone'],
                item['fromphone'],
                item['origin'],
                item['getdate'],
                item['content'],
            ))
        self.connect.commit()
        # with open('virtual.json', 'a', encoding='utf-8') as f:
        #     f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')

    def close_spider(self, spider):
        self.connect.close()
