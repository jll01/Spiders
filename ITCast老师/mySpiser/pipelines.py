# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class MyspiserPipeline(object):
    def process_item(self, item, spider):
        with open('teacher.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(item),ensure_ascii=False) + '\n')
