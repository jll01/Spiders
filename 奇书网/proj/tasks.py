#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   tasks.py
# @Time    :   2019/12/26 16:12
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import re
import requests
import time
import urllib3
import redis

from lxml import etree
from celery import group
from proj.app_test import app


urllib3.disable_warnings()

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
}
start_url = 'https://www.qisuu.la'
r = redis.StrictRedis(host='192.168.1.101', port=6379, db=4)

# trail=True如果启用，请求将跟踪由该任务启动的子任务，并且此信息将与结果（result.children）一起发送。
@app.task(trail=True)
def get_content(urls):
    '''并行调用任务,group一次创建多个任务'''
    group(C.s(title,url) for i in urls for title,url in i.items())()

@app.task(trail=True)
def C(title,url):
    '''返回此任务的签名对象，包装单个任务调用的参数和执行选项。'''
    parser.delay(title,url)

@app.task(trail=True)
def parser(classify, url):
    '''获取每个分类中具体书籍的详情url'''
    number = pagenum(url)
    # number = 1
    page = 1
    while page <= number:
        geturl = url + 'index_{}.html'.format(page)

        pagecon = requests.get(geturl, headers=headers, verify=False).text
        html = etree.HTML(pagecon)

        contents = html.xpath('//div[@class="wrap"]/div[@class="list"]/div[@class="listBox"]/ul/li')

        con = []
        for content in contents:
            detailurl = start_url + split_content(content.xpath('./a/@href'))
            con.append(ebookdetail(classify, url, detailurl))
        page += 1

def ebookdetail(classify, url, detailurl):
    '''进入到书籍详情链接后获取详情信息'''
    pagedetail = requests.get(detailurl, headers=headers, verify=False)
    if pagedetail.status_code == 200:
        htmldetail = etree.HTML(pagedetail.content)

        item = {}
        # 爬取时间
        item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 分类
        item['classify'] = classify
        # 分类url
        item['classify_url'] = url

        details = htmldetail.xpath(
            '//div[@class="show"]/div[@class="showBox"]/div[@class="detail"]/div[@class="detail_info"]/div[@class="detail_right"]')

        for detail in details:
            # 标题
            item['title'] = ''.join(detail.xpath('./h1/text()'))
            # 作者
            item['author'] = split_content(detail.xpath('./ul/li[6]/text()'))
            # 链接
            item['detail_url'] = detailurl
            # 阅读人数
            item['readnum'] = split_content(detail.xpath('./ul/li[1]/text()'))
            # 连载状态
            item['status'] = split_content(detail.xpath('./ul/li[5]/text()'))
            # 大小
            item['articlesize'] = split_content(detail.xpath('./ul/li[2]/text()'))
            # 更新时间
            item['updatetime'] = split_content(detail.xpath('./ul/li[4]/text()'))
            # 最新章节
            item['last'] = ''.join(detail.xpath('./ul/li[8]/a/text()'))

        # 图片
        item['image'] = start_url + split_content(htmldetail.xpath(
            '//div[@class="show"]/div[@class="showBox"]/div[@class="detail"]/div[@class="detail_pic"]/img/@src'))
        # 简介
        item['introduction'] = ''.join(
            htmldetail.xpath('//div[@class="show"]/div[@class="showBox mt20"]/div[@class="showInfo"]/p/text()'))
        # 在线阅读链接
        item['readonline'] = start_url + ''.join(htmldetail.xpath(
            '//div[@class="show"]/div[@class="showBox mt20"]/div[@class="showDown"]/ul/li[1]/a[@class="downButton"]/@href'))
        # 下载链接
        item['download'] = re_down(
            htmldetail.xpath('//div[@class="show"]//div[@class="showDown"]/ul/li[3]/script/text()'))

        print(item)
        saveredis(item)
        # return item
    else:
        print('一条数据提取错误！', pagedetail.status_code)

def pagenum(url):
    '''获取每个分类的总页数'''
    pageurl = requests.get(url, headers=headers, verify=False).text
    page_num = etree.HTML(pageurl)
    try:
        s = ''.join(page_num.xpath('//div[@class="wrap"]/div[@class="list"]//div[@class="tspage"]/text()'))
        num = int(re.findall(r'页次：1/(\d+)', s)[0])
    except Exception as e:
        print('页码总数提取错误:{}'.format(e))
        num = 0
    finally:
        return num

def saveredis(item):
    r.hmset(int(time.time() * 1000), item)

def split_content(con):
    '''分割提取小说作者大小等信息'''
    res = ''.join(con)
    try:
        return res.split('：')[1]
    except:
        return res

def read_num(num):
    '''阅读人数'''
    try:
        num = ''.join(num).split('：')[1]
        if len(num) != 0:
            return int(num)
        else:
            return 0
    except:
        return 0

def re_down(con):
    '''匹配下载链接'''
    try:
        return re.findall(r"(https://dzs.qisuu.la/.*)',", ''.join(con))[0]
    except:
        return ''