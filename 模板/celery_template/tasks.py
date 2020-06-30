#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   tasks.py
# @Time    :   2020/6/12 10:30
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import urllib3
import time

from celery import group
from fake_useragent import UserAgent
from lxml import etree
from celery_template.app import app


urllib3.disable_warnings()

base_url = 'https://www.xiaohua.com/duanzi?page={}'

# trail=True如果启用，请求将跟踪由该任务启动的子任务，并且此信息将与结果（result.children）一起发送。
@app.task(trail=True)
def get_content(page_num):
    """并行调用任务,group一次创建多个任务"""
    start = time.time()
    for i in range(1, page_num+1):
        group(C.s(base_url.format(i)))()
    print('总共花费时间：{}'.format(time.time()-start))


@app.task(trail=True)
def C(url):
    """返回此任务的签名对象，包装单个任务调用的参数和执行选项"""
    # delay是apply_async方法的别名,但接受的参数较为简单
    parser.delay(url)


@app.task(trail=True)
def parser(url):
    headers = {
        'User-Agent': UserAgent(verify_ssl=False).random
    }
    request = requests.get(url, headers=headers, verify=False)
    if request.status_code == 200:
        html = etree.HTML(request.text)
        contents = html.xpath('//div[@class="content-left"]/div[@class="one-cont"]')
        for content in contents:
            item = {}
            item['nickname'] = join_list(content.xpath('./div[1]/div/a/i/text()'))
            item['content'] = join_list(content.xpath('./p[@class="fonts"]/a/text()'))
            item['support'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
            item['not_support'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
            item['collect'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
            item['message'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
            item['share'] = int(join_list(content.xpath('./ul/li[1]/span/text()')))
            print(item)


def join_list(res):
    return ''.join(res)
