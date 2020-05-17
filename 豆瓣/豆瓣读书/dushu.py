#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   dushu.py
# @Time    :   2019-11-22 17:37:16
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import urllib3
import time
import random
import redis

from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor


class DouBanDuShu(object):
    def __init__(self):
        self.ua = UserAgent(verify_ssl=False)
        self.start_url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
        self.tag_urls = []
        self.tag_all_urls = []
        self.book_urls = []
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.con = redis.Redis(connection_pool=pool)

    def get_tag_urls(self):
        """获取豆瓣读书标签url"""
        headers = {
            'User-Agent': self.ua.random,
            'Cookie': 'bid=G9l-Rmd7Vwc; douban-fav-remind=1; gr_user_id=1ea52a62-cf13-4d9d-aa03-f3b5641d9313; _vwo_uuid_v2=DC45BDF89D6A26B905230357433358D30|4e54d88f2b0a98550c5fda10593f525d; viewed="25862578"; push_doumail_num=0; push_noty_num=0; __utmv=30149280.20446; ll="118391"; __utma=30149280.926321811.1573807683.1574085082.1574128508.7; __utmz=30149280.1574128508.7.5.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=0ce03953-2992-4c5a-8686-b9402e6d1249; gr_cs1_0ce03953-2992-4c5a-8686-b9402e6d1249=user_id%3A0; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1574128510%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; ap_v=0,6.0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_0ce03953-2992-4c5a-8686-b9402e6d1249=true; __utmc=30149280; __utmt_douban=1; __utma=81379588.495837698.1573956144.1574128510.1574130064.6; __utmc=81379588; __utmz=81379588.1574130064.6.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt=1; _pk_id.100001.3ac3=bed61ce839e643ae.1573956145.5.1574130092.1574082708.; __utmb=30149280.5.10.1574128508; __utmb=81379588.2.10.1574130064'
        }
        response = requests.get(self.start_url, headers=headers).text
        res = re.findall(r'<a href="(/tag/\w+)">(\w+)</a>', response)
        tag_urls = []
        for url_title in res:
            tag_urls.append({'tag': url_title[1], 'url': 'https://book.douban.com' + url_title[0]})
        return tag_urls

    def get_book_urls(self, item):
        """获取每个标签内中每个小说的详情url"""
        offset = 0
        while True:
            headers = {
                'User-Agent': self.ua.random,
                'Cookie': 'bid=G9l-Rmd7Vwc; douban-fav-remind=1; gr_user_id=1ea52a62-cf13-4d9d-aa03-f3b5641d9313; _vwo_uuid_v2=DC45BDF89D6A26B905230357433358D30|4e54d88f2b0a98550c5fda10593f525d; viewed="25862578"; push_doumail_num=0; push_noty_num=0; __utmv=30149280.20446; ll="118391"; __utma=30149280.926321811.1573807683.1574085082.1574128508.7; __utmz=30149280.1574128508.7.5.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=0ce03953-2992-4c5a-8686-b9402e6d1249; gr_cs1_0ce03953-2992-4c5a-8686-b9402e6d1249=user_id%3A0; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1574128510%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*; ap_v=0,6.0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_0ce03953-2992-4c5a-8686-b9402e6d1249=true; __utmc=30149280; __utmt_douban=1; __utma=81379588.495837698.1573956144.1574128510.1574130064.6; __utmc=81379588; __utmz=81379588.1574130064.6.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt=1; _pk_id.100001.3ac3=bed61ce839e643ae.1573956145.5.1574130092.1574082708.; __utmb=30149280.5.10.1574128508; __utmb=81379588.2.10.1574130064'
            }
            response = requests.get(item['url'] + '?start={}&type=T'.format(offset), headers=headers).text
            book_urls = re.findall(r'<a href="(.*?)"\s+title=".*?"', response)
            if len(book_urls) != 0:
                for book_url in book_urls:
                    self.con.sadd("douban_book_urls" + ':' + item['tag'], str({'tag': item['tag'], 'url': book_url}))

                offset += 20
                time.sleep(random.uniform(0.5, 1))
            else:
                break

    def book_detail(self, tag_url):
        """提取每本小说的详细内容"""
        item = {}
        headers = {
            'User-Agent': self.ua.random,
            'Cookie': 'bid=G9l-Rmd7Vwc; douban-fav-remind=1; gr_user_id=1ea52a62-cf13-4d9d-aa03-f3b5641d9313; _vwo_uuid_v2=DC45BDF89D6A26B905230357433358D30|4e54d88f2b0a98550c5fda10593f525d; viewed="25862578"; __utmc=30149280; __utmz=30149280.1574068696.3.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmc=81379588; __utmz=81379588.1574068696.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; push_doumail_num=0; push_noty_num=0; ap_v=0,6.0; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1574079526%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DJbVBfyAkgTmcUAFs-JCtUMZnijDPOLgOaZbV9HcvYUxajR7bOVVF5fx8Urt8VI2N%26wd%3D%26eqid%3Db23c92be001ab07f000000035dd261d5%22%5D; _pk_ses.100001.3ac3=*; __utma=30149280.926321811.1573807683.1574074060.1574079526.5; __utma=81379588.495837698.1573956144.1574074060.1574079526.4; dbcl2="204467403:EPEjVjuwIFY"; ck=Vm5N; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=0fccd68c-6625-4993-9160-8cfd13c3228c; gr_cs1_0fccd68c-6625-4993-9160-8cfd13c3228c=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_0fccd68c-6625-4993-9160-8cfd13c3228c=true; _pk_id.100001.3ac3=bed61ce839e643ae.1573956145.4.1574080880.1574076660.; __utmb=30149280.42.10.1574079526; __utmb=81379588.42.10.1574079526'
        }
        url = tag_url['url'].decode('utf-8')
        tag = tag_url['tag']
        response = requests.get(url, headers=headers).text.replace('\n', '').replace(' ', '')

        item['tag'] = tag
        item['book_url'] = url
        item['title'] = ''.join(re.findall(r'<spanproperty="v:itemreviewed">(.*?)</span>', response))
        item['author'] = ''.join(re.findall(r'<spanclass="pl">作者:.*?">(.*?)</a><br>', response))
        item['publish'] = ''.join(re.findall(r'<spanclass="pl">出版社:</span>(\w+)<br/>', response))
        item['year'] = ''.join(re.findall(r'<spanclass="pl">出版年:</span>(.*?)<br/>', response))
        item['page_num'] = ''.join(re.findall(r'<spanclass="pl">页数:</span>(.*?)<br/>', response))
        item['price'] = ''.join(re.findall(r'<spanclass="pl">定价:</span>(.*?)元<br/>', response))
        item['art'] = ''.join(re.findall(r'<spanclass="pl">装帧:</span>(.*?)<br/>', response))
        item['series'] = ''.join(re.findall(r'<spanclass="pl">丛书:.*?">(.*?)</a><br>', response))
        item['ISBN'] = ''.join(re.findall(r'<spanclass="pl">ISBN:</span>(.*?)<br/>', response))
        item['score'] = ''.join(re.findall(r'<strongclass="llrating_num"property="v:average">(.*?)</strong>', response))
        item['people_number'] = ''.join(re.findall(r'<spanproperty="v:votes">(.*?)</span>', response))
        item['introduce'] = ''.join(re.findall(r'<divclass="intro"><p>(.*?)</p></div>', response))
        print(item)

        self.con.sadd("douban_book_detail" + ':' + tag, str(item))
        time.sleep(random.uniform(0.5, 1))

    def main(self):
        tag_urls = self.get_tag_urls()
        for tag_url in tag_urls:
            self.get_book_urls(tag_url)

        tags = ['小说', '外国文学', '文学', '经典', '中国文学', '随笔', '日本文学', '散文', '村上春树', '诗歌', '童话', '名著', '儿童文学', '古典文学', '余华', '王小波', '杂文', '张爱玲', '当代文学', '外国名著', '钱钟书', '鲁迅', '诗词', '茨威格', '杜拉斯', '港台', '漫画', '推理', '绘本', '青春', '东野圭吾', '悬疑', '科幻', '言情', '奇幻', '推理小说', '武侠', '日本漫画', '耽美', '韩寒', '网络小说', '亦舒', '三毛', '科幻小说', '金庸', '安妮宝贝', '穿越', '郭敬明', '轻小说', '魔幻', '青春文学', '几米', '幾米', '张小娴', '古龙', '高木直子', '校园', '沧月', '余秋雨', '落落', '历史', '心理学', '哲学', '社会学', '传记', '文化', '艺术', '社会', '设计', '政治', '宗教', '建筑', '政治学', '电影', '数学', '中国历史', '回忆录', '思想', '国学', '人物传记', '艺术史', '人文', '音乐', '绘画', '戏剧', '西方哲学', '近代史', '二战', '军事', '佛教', '考古', '自由主义', '美术', '爱情', '成长', '生活', '旅行', '心理', '励志', '女性', '摄影', '教育', '职场', '美食', '游记', '灵修', '健康', '情感', '人际关系', '两性', '手工', '养生', '家居', '自助游', '经济学', '管理', '经济', '商业', '金融', '投资', '营销', '理财', '创业', '股票', '广告', '企业史', '策划', '科普', '互联网', '编程', '科学', '交互设计', '用户体验', '算法', '科技', 'web', '交互', '通信', 'UE', 'UCD', '神经网络', '程序']
        urls_list = []
        for tag in tags:
            urls_list.extend(list(self.con.smembers("doubandushu" + ':' + tag)))

        pool = ThreadPoolExecutor(5)
        for tag_url in urls_list:
            pool.submit(self.book_detail(tag_url))

        pool.shutdown()


if __name__ == '__main__':
    urllib3.disable_warnings()

    db = DouBanDuShu()
    db.main()

