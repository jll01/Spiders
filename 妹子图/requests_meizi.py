#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   requests_meizi.py
# @Time    :   2019/10/25 20:28
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import urllib3
import os

from lxml import etree
from threading import Thread


class MeiZi(object):
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        }
        self.get_url = 'https://www.mzitu.com/page/{}/'
        self.page = 1

    def geturl(self):
        while True:
            content = requests.get(self.get_url.format(self.page), headers=self.headers, verify=False).text
            html = etree.HTML(content)
            urls = html.xpath('//ul[@id="pins"]/li/span/a/@href')
            titles = html.xpath('//ul[@id="pins"]/li/span/a/text()')
            numbers = html.xpath('//div[@class="nav-links"]/a/text()')[-2]
            t = []
            for url, title in zip(urls, titles):
                file = os.path.join(os.getcwd(), 'images', title)
                if not os.path.exists(file):
                    os.makedirs(file)

                self.getdata(url, title)
                # th = Thread(target=self.getdata, args=(url, title))
                # th.start()
                # t.append(th)

            for i in t:
                i.join()

            if self.page < int(numbers):
                self.page += 1
                # time.sleep(random.uniform(3, 5))
            else:
                break

    def getdata(self, url, title):
        num = 1
        while True:
            new_url = url + '/' + str(num)
            try:
                data_image = requests.get(new_url, headers=self.headers, verify=False, timeout=500)
                html_image = etree.HTML(data_image.text)
                url_image = html_image.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
                all_num = html_image.xpath('//div[@class="pagenavi"]/a/span/text()')[-2]
                headers = {
                    'Referer': url,
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
                }
                try:
                    datas = requests.get(url_image, headers=headers, verify=False, timeout=500).content
                    file_path = os.path.join(os.getcwd(), 'images', title)
                    with open(file_path + '/' + str(num) + '.jpg', 'wb') as f:
                        f.write(datas)
                    print(url_image, '{}下载成功'.format(title + '/' + str(num)))
                except:
                    pass
            except Exception as e:
                print('{}错误{} {}！'.format(new_url, e, data_image.status_code))
                num += 1
            else:
                if num < int(all_num):
                    num += 1
                    time.sleep(random.uniform(0.5, 1))
                else:
                    break

    def main(self):
        self.geturl()


if __name__ == '__main__':
    urllib3.disable_warnings()

    mz = MeiZi()
    mz.main()
