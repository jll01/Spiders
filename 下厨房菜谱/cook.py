#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   cook.py
# @Time    :   2020/5/20 16:55
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import time
import random
import json

from fake_useragent import UserAgent
from lxml import etree


class Cook(object):
    def __init__(self, key_word):
        # 搜索的菜谱名
        self.keyword = key_word
        # 查找搜索url
        self.search_url = '''http://www.xiachufang.com/search/?keyword={}&cat=1001'''
        # 页码增量
        self.page_num = 1
        self.detail = '''http://www.xiachufang.com{}'''

    def get_search_url(self):
        """
        获取搜索菜谱的结果url
        :return: 匹配到的url
        """
        headers = {
            'User-Agent': UserAgent().random,
            'Cookie': 'bid=VtyW3jhk; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217231303e681f-00a7c13bbcc1f-f7d1d38-1327104-17231303e696a0%22%2C%22%24device_id%22%3A%2217231303e681f-00a7c13bbcc1f-f7d1d38-1327104-17231303e696a0%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; __utma=177678124.387019044.1589963145.1589963145.1589963145.1; __utmc=177678124; __utmz=177678124.1589963145.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_ecd4feb5c351cc02583045a5813b5142=1589963145; Hm_lpvt_ecd4feb5c351cc02583045a5813b5142=1589967665; __utmt=1; __utmb=177678124.32.10.1589963145'
        }
        source = requests.get(self.search_url.format(self.keyword), headers=headers).text

        return ''.join(re.findall(r'<link rel="canonical" href="(.*?)">', source, re.DOTALL))

    def get_source(self):
        """
        获取每个菜谱的url
        :return:
        """
        start_url = self.get_search_url()
        if start_url:
            headers = {
                'User-Agent': UserAgent().random,
                'Cookie': 'bid=VtyW3jhk; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217231303e681f-00a7c13bbcc1f-f7d1d38-1327104-17231303e696a0%22%2C%22%24device_id%22%3A%2217231303e681f-00a7c13bbcc1f-f7d1d38-1327104-17231303e696a0%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; __utma=177678124.387019044.1589963145.1589963145.1589963145.1; __utmc=177678124; __utmz=177678124.1589963145.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_ecd4feb5c351cc02583045a5813b5142=1589963145; Hm_lpvt_ecd4feb5c351cc02583045a5813b5142=1589967665; __utmt=1; __utmb=177678124.32.10.1589963145'
            }
            while True:
                req_url = start_url + '?page={}'.format(self.page_num)
                source = requests.get(req_url, headers=headers)
                if source.status_code == 200:
                    html = etree.HTML(source.text)
                    detail_urls = html.xpath('//ul[@class="list"]/li//p[@class="name"]/a/@href')
                    for url in detail_urls:
                        self.get_detail(self.detail.format(url))
                        time.sleep(random.uniform(0.8, 1.5))

                    self.page_num += 1

                elif source.status_code == 404:
                    break
                else:
                    print('{}第{}页获取失败！'.format(req_url, self.page_num))

                time.sleep(random.uniform(3, 5))

        else:
            print('获取搜索url失败！')

    def get_detail(self, url):
        """
        获取每个菜谱的内容
        :param url: 每个菜谱的url
        :return:
        """
        headers = {
            'User-Agent': UserAgent().random,
            'Cookie': 'bid=VtyW3jhk; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217231303e681f-00a7c13bbcc1f-f7d1d38-1327104-17231303e696a0%22%2C%22%24device_id%22%3A%2217231303e681f-00a7c13bbcc1f-f7d1d38-1327104-17231303e696a0%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; __utma=177678124.387019044.1589963145.1589963145.1589963145.1; __utmc=177678124; __utmz=177678124.1589963145.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_ecd4feb5c351cc02583045a5813b5142=1589963145; Hm_lpvt_ecd4feb5c351cc02583045a5813b5142=1589970825; __utmb=177678124.46.10.1589963145'
        }
        detail_page = requests.get(url, headers=headers)
        if detail_page.status_code == 200:
            detail_html = etree.HTML(detail_page.text)
            item = dict()
            ings = dict()
            desc = dict()
            # 每个菜谱的url
            item['url'] = url
            # 菜谱名
            item['title'] = self.join_list(detail_html.xpath('//h1[@class="page-title"]/text()'))
            # 评分
            item['ratingValue'] = self.join_list(detail_html.xpath('//span[@itemprop="ratingValue"]/text()'))
            # 做过的人数
            item['cooked_num'] = self.join_list(detail_html.xpath('//div[contains(@class,"cooked")]/span[@class="number"]/text()'))
            # 菜谱发布时间
            item['published'] = self.join_list(detail_html.xpath('//div[@class="time"]/span[@itemprop="datePublished"]/text()'))
            # 收藏人数
            item['collect'] = self.join_list(detail_html.xpath('//div[@class="pv"]/text()'))[:-3]
            # 厨师url
            item['author_url'] = self.detail.format(self.join_list(detail_html.xpath('//div[@class="author"]/a/@href')))
            # 厨师昵称
            item['uname'] = self.join_list(detail_html.xpath('//div[@class="author"]/a/@title'))
            # 厨师头像
            item['author_img'] = self.join_list(detail_html.xpath('//div[@class="author"]/a/img/@src'))
            # 菜谱描述
            item['description'] = self.join_list(detail_html.xpath('//div[@itemprop="description"]/text()'))
            # 用料名和数量
            ings_names = detail_html.xpath('//tr[@itemprop="recipeIngredient"]/td[@class="name"]/a/text()')
            units = detail_html.xpath('//tr[@itemprop="recipeIngredient"]/td[@class="unit"]/text()')
            for name, unit in zip(ings_names, units):
                ings[name] = unit.strip()
            item['ings'] = ings

            # 步骤
            steps = detail_html.xpath('//div[@class="steps"]/ol/li/p[@class="text"]/text()')
            # 每一个步骤的图片
            images = detail_html.xpath('//div[@class="steps"]/ol/li/img/@src')
            # 步骤名
            alts = detail_html.xpath('//div[@class="steps"]/ol/li/img/@alt')
            for step, image, alt in zip(steps, images, alts):
                desc[alt] = {'step_desc': step, 'result_image': image}
            item['steps'] = desc

            print(item)
            # 保存
            self.save_item(item)
        else:
            print('{}获取失败！'.format(url))

    def save_item(self, item):
        """
        保存到本地json文件中
        :param item: 每个菜谱的内容
        :return:
        """
        with open('{}.json'.format(self.keyword), 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    @staticmethod
    def join_list(in_list):
        """
        拼接列表
        :param in_list: 要拼接的列表
        :return: 拼接后的字符串
        """
        return ''.join(in_list).strip()

    def main(self):
        self.get_source()


if __name__ == '__main__':
    keyword = input('请输入搜索的菜谱: ')
    cook = Cook(keyword)
    cook.main()
