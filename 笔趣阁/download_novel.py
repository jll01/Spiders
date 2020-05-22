#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   download_novel.py
# @Time    :   2020/5/22 15:55
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import urllib3
import io
import sys

from lxml import etree
from fake_useragent import UserAgent


class Novel(object):
    def __init__(self, keyword):
        # 下载的书名
        self.keyword = keyword
        self.search_url = '''https://so.biqusoso.com/s.php?ie=utf-8&siteid=biqukan.com&q={}'''
        # 保存搜索到的信息
        self.save_search = {}
        # 合并每章节的url
        self.novel_content_url = 'https://www.biqukan.com{}'

    def get_search_result(self):
        """
        搜索要下载的书名，并将搜索结果显示出来
        :return:
        """
        headers = {
            'User-Agent': UserAgent().random
        }
        source = requests.get(self.search_url.format(self.keyword), headers=headers).text
        html = etree.HTML(source)
        # 序号
        order_nums = html.xpath('//div[@id="search-main"]//ul/li/span[@class="s1"]/text()')
        # 书名
        titles = html.xpath('//div[@id="search-main"]//ul/li/span[@class="s2"]/a/text()')
        # 链接
        urls = html.xpath('//div[@id="search-main"]//ul/li/span[@class="s2"]/a/@href')
        # 作者
        names = html.xpath('//div[@id="search-main"]//ul/li/span[@class="s4"]/text()')

        num, title, url, name = '序号', '作品名称', '链接', '作者'

        print("{num:<6}\t{title:<{len1}}\t{url:<{len2}}\t{name:<25}".format(
            num=num, title=title, url=url, name=name, len1=self.pad_len(title, 35), len2=self.pad_len(url, 25)))

        for num, title, url, name in zip(order_nums, titles, urls, names):
            self.save_search[num] = url
            print("{num:<6}\t{title:<{len1}}\t{url:<{len2}}\t{name:<25}".format(
                num=num, title=title, url=url, name=name, len1=self.pad_len(title, 35), len2=self.pad_len(url, 25)))

    def get_page(self):
        """
        输入下载的序号，获得该序号对应小说的url，请求得到该小说所有章节的url
        :return:
        """
        num = input('请输入要下载的小说序号：').strip()
        req_url = self.save_search.get(num, 0)
        if req_url != 0:
            page = requests.get(req_url, headers={'User-Agent': UserAgent().random}).content
            page_html = etree.HTML(page)
            urls = page_html.xpath('//div[@class="listmain"]/dl/dd/a/@href')
            for url in urls[12:]:
                self.get_novel_content(url)
                time.sleep(random.uniform(0.8, 1))
        else:
            print('未找到输入！请检查后再下载！')

    def get_novel_content(self, url):
        """
        获取该章节的标题和内容
        :param url: 章节的链接
        :return:
        """
        url = self.novel_content_url.format(url)
        try:
            source = requests.get(url, headers={'User-Agent': UserAgent().random})
            contents = etree.HTML(source.content)
            # 标题
            title = contents.xpath('//div[@class="content"]/h1/text()')
            # 内容
            content = contents.xpath('//div[@id="content"]/text()')

            title = ''.join(title).replace('\xa0' * 8, '').replace(r'\xd2', '')
            content = ''.join(content).replace('\xa0' * 8, '').replace(r'\xd2', '')

            self.save_content(title, content)
        except Exception as e:
            print('{}请求错误！'.format(url))

    def save_content(self, title, content):
        """
        保存到本地
        :param title: 标题
        :param content: 内容
        :return:
        """
        print('正在下载：{}'.format(title))
        try:
            with open('{}.txt'.format(self.keyword), 'a', encoding='utf-8') as f:
                f.write(title.replace('\xa0', ''))
                f.write('\n')
                f.write(content.replace('\xa0', ''))
                f.write('\n\n')
        except Exception as e:
            print('{}下载错误！'.format(title))

    @staticmethod
    def pad_len(string, length):
        """
        print字符串对齐
        :param string:  字符串
        :param length:  对齐长度
        :return:    补齐的长度
        """
        return length - len(string.encode('GBK')) + len(string)

    def main(self):
        self.get_search_result()
        self.get_page()


if __name__ == '__main__':
    urllib3.disable_warnings()
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
    novel = Novel('斗罗大陆')
    novel.main()
