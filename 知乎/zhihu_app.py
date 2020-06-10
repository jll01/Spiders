#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   test.py
# @Time    :   2020/6/10 16:05
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import urllib3
import json


class ZhiHu(object):
    def __init__(self, page_number):
        self.url = '''https://api.zhihu.com/topstory/recommend?session_token={}&page_number={}&limit={}&action=down&after_id={}&ad_interval={}&start_type=warm'''
        self.page_number = page_number
        self.session_token = '4716c18b61d12bfea5513bde58eaa3e3'
        self.limit = 6
        self.ad_interval = -1
        self.headers = {
            'User-Agent': 'com.zhihu.android/Futureve/6.43.0 Mozilla/5.0 (Linux; Android 5.1.1; vivo Y51A Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36',
            'Cookie': 'KLBRSID=4efa8d1879cb42f8c5b48fe9f8d37c16|1591777512|1591777199; z_c0=2|1:0|10:1591777204|4:z_c0|92:Z3QyLjBBQUFBQUJOWkxSTVFNdTZIc0d0d0FBQUFBQXhOVlFKZ0FnQk5KUFRsdzFQVk9Jc3RnUzVCUkNsMWZfRnZzZz09|513cb3e4105daff231ab8b32310f5b1c98f0fcbf6f5e20c147caee3a0ea1a355; _xsrf=63PXAE89Hn09A7y9H0xRGAfIgX7ZIiLJ',
        }

    def get_content(self):
        for i in range(2, self.page_number+2):

            after_id = (i-1) * self.limit + self.ad_interval
            try:
                get_data = requests.get(self.url.format(self.session_token, i, self.limit, after_id, self.ad_interval), headers=self.headers, verify=False).json()
                dll_data = get_data['data']
                for data in dll_data:
                    item = dict()
                    item['id'] = data.get('id', '')
                    item['type'] = data.get('type', '')
                    item['created_time'] = self.time2str(data.get('created_time', int(time.time())))
                    item['updated_time'] = self.time2str(data.get('updated_time', int(time.time())))
                    target = data['target']
                    item['target_id'] = target.get('id', '')
                    item['target_type'] = target.get('type', '')
                    item['target_url'] = target.get('url', '')
                    item['target_created_time'] = self.time2str(target.get('created_time', int(time.time())))
                    item['target_updated_time'] = self.time2str(target.get('updated_time', int(time.time())))
                    item['target_voteup_count'] = target.get('voteup_count', '')
                    item['target_thanks_count'] = target.get('thanks_count', '')
                    item['target_comment_count'] = target.get('comment_count', '')
                    author = target['author']
                    item['author_id'] = author.get('id', '')
                    item['author_type'] = author.get('type', '')
                    item['author_url'] = author.get('url', '')
                    item['author_name'] = author.get('name', '')
                    item['author_headline'] = author.get('headline', '')
                    item['author_avatar_url'] = author.get('avatar_url', '')
                    try:
                        question = target['question']
                        item['question_id'] = question.get('id', '')
                        item['question_type'] = question.get('type', '')
                        item['question_url'] = question.get('url', '')
                        item['question_title'] = question.get('title', '')
                        item['question_created'] = question.get('created', '')
                        item['question_answer_count'] = question.get('answer_count', '')
                        item['question_follower_count'] = question.get('follower_count', '')
                        item['question_comment_count'] = question.get('comment_count', '')
                    except Exception as e:
                        item['question_id'] = ''
                        item['question_type'] = ''
                        item['question_url'] = ''
                        item['question_title'] = ''
                        item['question_created'] = ''
                        item['question_answer_count'] = ''
                        item['question_follower_count'] = ''
                        item['question_comment_count'] = ''
                        item['target_excerpt'] = ''

                    item['target_excerpt_new'] = target.get('excerpt_new', '')
                    item['target_visited_count'] = target.get('visited_count', '')
                    item['target_excerpt'] = target.get('excerpt', '')

                    print(item)
                    self.save2json(item)
                time.sleep(random.uniform(1, 1.5))
            except Exception as e:
                print(f'获取错误{e}')
                break

    @staticmethod
    def time2str(inner):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inner))

    @staticmethod
    def save2json(item):
        with open('zh.json', 'a+', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def main(self):
        self.get_content()


if __name__ == '__main__':
    urllib3.disable_warnings()
    zh = ZhiHu(int(input('请输入页码：')))
    zh.main()
