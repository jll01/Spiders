#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   bianbizhi.py
# @Time    :   2019/10/26 9:42
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import os
import re


class Bizhi(object):
    def __init__(self):
        self.start_url = 'http://pic.netbian.com/index_{}.html'
        self.page = 1
        self.headers = {
            # 'Host': 'pic.netbian.com',
            # 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        }

    def get_url(self):
        self.create_path()
        while True:
            if self.page == 1:
                req_url = 'http://pic.netbian.com/index.html'
            else:
                req_url = self.start_url.format(self.page)
            req = requests.get(req_url, headers=self.headers)
            if req.status_code == 404:
                break
            contents = re.findall(r'<li><a.*?><img\s+src=\"(.*?)\"\s+alt=\"(.*?)\".*?</b></a></li>', req.content.decode('gb2312'))
            url_str = 'http://pic.netbian.com'
            for content in contents:
                url = url_str + content[0]
                title = content[1]
                self.save(url, title)
                time.sleep(random.uniform(0.1, 0.5))
            self.page += 1
            time.sleep(random.uniform(2, 4))

    def save(self, url, title):
        image = requests.get(url, headers=self.headers, timeout=5).content
        self.create_path()
        title = re.sub(r'[: \ / * ? < > | " ]', '', title)
        file_path = os.path.join(os.getcwd(), 'images', title + '.jpg')
        with open(file_path, 'wb') as f:
            f.write(image)
        print('{} {} 下载完成！'.format(url, title))

    def create_path(self):
        file = os.path.join(os.getcwd(), 'images')
        if not os.path.exists(file):
            os.mkdir(file)

    def main(self):
        self.get_url()


if __name__ == '__main__':
    bz = Bizhi()
    bz.main()
