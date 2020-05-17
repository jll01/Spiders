# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql


class ZonghengPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def process_item(self, item, spider):
        # with open('纵横中文.json', 'a', encoding='utf-8') as file:
        #     file.write(json.dumps(dict(item), ensure_ascii=False) + '\n')
        self.cur.execute(
            """insert into zongheng (spider_time, url, title, author, author_url, category, category_url, status, update_time, intro, book_update, update_url, 
            number, all_recommend, click_num, week_recommend) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                item['spider_time'],
                item['url'],
                item['title'],
                item['author'],
                item['author_url'],
                item['category'],
                item['category_url'],
                item['status'],
                item['update_time'],
                item['intro'],
                item['book_update'],
                item['update_url'],
                item['number'],
                item['all_recommend'],
                item['click_num'],
                item['week_recommend']
            )
        )
        self.connect.commit()

    def close_spider(self, spider):
        self.connect.close()
