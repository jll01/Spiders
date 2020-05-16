#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   ebook.py
# @Time    :   2019/9/2 9:37
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from gevent import monkey
monkey.patch_all()

import gevent
import requests
import re
import time
import urllib3
import random
import pymysql
import math

from lxml import etree


class qishuebook(object):
    '''奇书网小说爬虫'''
    def __init__(self):
        self.header = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
            "Opera/8.0 (Windows NT 5.1; U; en)",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
        ]
        proxies = [
            '117.191.11.113:80',
            '117.191.11.80:80',
            '117.191.11.109:8080',
            '39.135.24.11:80',
            '117.191.11.109:80',
            '117.191.11.108:8080',
            '117.191.11.110:8080',
        ]
        self.headers = {
            'User-Agent': random.choice(self.header)
        }
        self.proxies = {
            'http': random.choice(proxies)
        }
        self.start_url = 'https://www.qisuu.la'
        # 存储分类的url
        self.savestarturl = []
        self.notspider = []

    def startrequests(self):
        '''获取起始页分类的链接和名称'''
        page = requests.get(self.start_url, headers=self.headers, proxies=self.proxies, verify=False, timeout=10).text
        page_content = etree.HTML(page)
        classifyurls = page_content.xpath('//div[@class="wrap header"]/div/a/@href')
        titles = page_content.xpath('//div[@class="wrap header"]/div/a/text()')

        for title, url in zip(titles,classifyurls):
            item = {}
            item[title] = self.start_url + url
            self.savestarturl.append(item)

    def ebookcontent(self):
        '''使用多线程对每个分类'''
        for i in range(math.ceil(len(self.savestarturl[1:])/4)):
            th = []
            for target in self.savestarturl[(1+i*4):(1+(i+1)*4)]:
                classify = list(target.keys())[0]
                url = list(target.values())[0]
                # self.getcontent(classify, url)
                th.append(gevent.spawn(self.getcontent,classify,url))

            gevent.joinall(th)

    def getcontent(self, classify,url):
        '''获取每个分类中具体书籍的详情url'''
        number = self.pagenum(url)
        # number = 3
        page = 1
        while page <= number:
            geturl = url + 'index_{}.html'.format(page)

            pagecon = requests.get(geturl, headers=self.headers, proxies=self.proxies, verify=False, timeout=10).text
            html = etree.HTML(pagecon)

            contents = html.xpath('//div[@class="wrap"]/div[@class="list"]/div[@class="listBox"]/ul/li')
            for i in range(math.ceil(len(contents)/5)):
                detailth = []
                for content in contents[i*5:(i+1)*5]:
                    detailurl = self.start_url + self.split_content(content.xpath('./a/@href'))
                    detailth.append(gevent.spawn(self.ebookdetail,classify,url,detailurl,page))

                gevent.joinall(detailth, timeout=15)

            time.sleep(random.uniform(5, 8))
            page += 1

    def ebookdetail(self,classify,url,detailurl,page):
        '''进入到书籍详情链接后获取详情信息'''
        pagedetail = requests.get(detailurl, headers=self.headers, proxies=self.proxies, timeout=15, verify=False)
        # print(classify,pagedetail.status_code, page, detailurl)
        if pagedetail.status_code == 200:
            htmldetail = etree.HTML(pagedetail.content)

            item = {}
            # 爬取时间
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # 分类
            item['classify'] = classify
            # 分类url
            item['classify_url'] = url

            details = htmldetail.xpath('//div[@class="show"]/div[@class="showBox"]/div[@class="detail"]/div[@class="detail_info"]/div[@class="detail_right"]')

            for detail in details:
                # 标题
                item['title'] = ''.join(detail.xpath('./h1/text()'))
                # 作者
                item['author'] = self.split_content(detail.xpath('./ul/li[6]/text()'))
                # 链接
                item['detail_url'] = detailurl
                # 阅读人数
                item['readnum'] = self.split_content(detail.xpath('./ul/li[1]/text()'))
                # 连载状态
                item['status'] = self.split_content(detail.xpath('./ul/li[5]/text()'))
                # 大小
                item['articlesize'] = self.split_content(detail.xpath('./ul/li[2]/text()'))
                # 更新时间
                item['updatetime'] = self.split_content(detail.xpath('./ul/li[4]/text()'))
                # 最新章节
                item['last'] = ''.join(detail.xpath('./ul/li[8]/a/text()'))

            # 图片
            item['image'] = self.start_url + self.split_content(htmldetail.xpath('//div[@class="show"]/div[@class="showBox"]/div[@class="detail"]/div[@class="detail_pic"]/img/@src'))
            # 简介
            item['introduction'] = ''.join(htmldetail.xpath('//div[@class="show"]/div[@class="showBox mt20"]/div[@class="showInfo"]/p/text()'))
            # 在线阅读链接
            item['readonline'] = self.start_url +  ''.join(htmldetail.xpath('//div[@class="show"]/div[@class="showBox mt20"]/div[@class="showDown"]/ul/li[1]/a[@class="downButton"]/@href'))
            # 下载链接
            item['download'] = self.re_down(htmldetail.xpath('//div[@class="show"]//div[@class="showDown"]/ul/li[3]/script/text()'))

            print(page,item)
            # gevent.joinall([
            #     gevent.spawn(self.saveebook, item),
            # ])
            self.saveebook(item)

        else:
            self.notspider.append({detailurl:[classify,url,page]})
            print('一条数据提取错误！',pagedetail.status_code)

    def pagenum(self, url):
        '''获取每个分类的总页数'''
        pageurl = requests.get(url, headers=self.headers, proxies=self.proxies, verify=False, timeout=10).text
        page_num = etree.HTML(pageurl)
        try:
            s = ''.join(page_num.xpath('//div[@class="wrap"]/div[@class="list"]//div[@class="tspage"]/text()'))
            num = int(re.findall(r'页次：1/(\d+)', s)[0])
        except Exception as e:
            print('页码总数提取错误:{}'.format(e))
            num = 0
        finally:
            return num

    def split_content(self,con):
        '''分割提取小说作者大小等信息'''
        res = ''.join(con)
        try:
            return res.split('：')[1]
        except:
            return res

    def read_num(self,num):
        '''阅读人数'''
        try:
            num = ''.join(num).split('：')[1]
            if len(num) != 0:
                return int(num)
            else:
                return 0
        except:
            return 0

    def re_down(self,con):
        '''匹配下载链接'''
        try:
            return re.findall(r"(https://dzs.qisuu.la/.*)',", ''.join(con))[0]
        except:
            return ''

    def saveebook(self,item):
        connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        cur = connect.cursor()
        try:
            cur.execute(
                '''insert into qishuebook (spidertime,classify,classify_url,title,author,readnum,status,articlesize,updatetime,detail_url,image,last,introduction,readonline,download) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['spidertime'],
                    item['classify'],
                    item['classify_url'],
                    item['title'],
                    item['author'],
                    item['readnum'],
                    item['status'],
                    item['articlesize'],
                    item['updatetime'],
                    item['detail_url'],
                    item['image'],
                    item['last'],
                    item['introduction'][:2000],
                    item['readonline'],
                    item['download'],
                )
            )
            connect.commit()
            cur.close()
            connect.close()
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))

    def main(self):
        self.startrequests()
        self.ebookcontent()
        print('-'*30 + '主程序爬取信息完成，将对未提取到的信息进行重新提取！' +'-'*30)

        n = 1
        while len(self.notspider) != 0:
            s = []
            print('*' * 30 + '第{}次重试！'.format(n) + '*' * 30)
            for i in range(math.ceil(len(self.notspider)/4)):
                for item in self.notspider[i*4:(i+1)*4]:
                    s.append(gevent.spawn(self.ebookdetail,list(item.values())[0][0],list(item.values())[0][1],list(item.keys())[0],list(item.values())[0][2]))
                    self.notspider.remove(item)
                gevent.joinall(s)

            n += 1

        print('所有信息提取完成！')


if __name__ == '__main__':

    urllib3.disable_warnings()

    eb = qishuebook()
    eb.main()
