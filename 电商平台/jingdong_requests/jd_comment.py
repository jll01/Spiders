#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   jd_comment.py
# @Time    :   2019/8/1 17:31
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import time
import json
import random
import urllib3
import pymysql

from urllib import parse
from lxml import etree


class JingDong(object):

    def __init__(self,kw):
        self.prv_url = 'https://search.jd.com/Search?'
        self.after_url = 'https://search.jd.com/s_new.php?'
        # 评论url
        self.url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv{}&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'
        self.session = requests.session()
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        ]
        self.headers = {
            'Referer': '',
            'User-Agent': random.choice(self.user_agent),
        }
        # IP代理
        self.ip = [
            '117.191.11.113:80',
            '117.191.11.109:8080',
            '117.191.11.80:80',
            '117.191.11.76:8080',
            '117.191.11.80:80',
            '117.191.11.108:80',
            '117.191.11.111:80',
            '117.191.11.109:8080',
            '39.135.24.11:80',
            '117.191.11.109:80',
            '117.191.11.108:8080',
            '117.191.11.110:8080',
            '39.137.69.7:80',
            '39.137.69.7:8080',
            '39.137.69.10:8080'
        ]
        self.proxies = {
            'http': random.choice(self.ip),
        }

        self.kw = kw
        self.page_num = 1

        self.shop_ip_list = []

        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def get_page_num(self):
        '''获取当前商品有多少页'''
        params = {
            'keyword': self.kw,
            'enc': 'utf-8',
            'page': '1',
        }
        response = requests.get(self.prv_url + parse.urlencode(params), headers=self.headers, verify=False).content
        html = etree.HTML(response)
        page = html.xpath('//div[@id="J_topPage"]/span/i/text()')[0]
        return page

    def get_page_html(self):
        '''只获取页面html'''
        page = int(self.get_page_num())
        num = 1
        print('{}商品总共有{}页'.format(self.kw, page))
        while True:
            '''前30条信息'''
            params = {
                'keyword': self.kw,
                'enc': 'utf-8',
                'page': self.page_num,
            }
            p_url = self.prv_url + parse.urlencode(params)
            response = requests.get(p_url, headers=self.headers, verify=False).content
            try:
                html = etree.HTML(response)
            except Exception as e:
                pass
            else:
                self.get_shop_id(html)

            '''后30条信息'''
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                "referer": p_url,
            }
            af_params = {
                'keyword': self.kw,
                'enc': 'utf-8',
                'page': self.page_num + 1,
                'qrst': '1',
                'rt': '1',
                'stop': '1',
                'vt': '2',
                'wq': self.kw,
                'scrolling': 'y',
                'log_id': round(time.time(), 5),
            }
            af_url = self.after_url + parse.urlencode(af_params)
            af_response = requests.get(af_url, headers=headers, verify=False).content
            try:
                af_html = etree.HTML(af_response)
            except Exception as e:
                pass
            else:
                self.get_shop_id(af_html)

            if self.page_num < page * 2 - 1:
                print('第{}页商品ID提取完成！'.format(num))
                self.page_num += 2
                num += 1
            else:
                break
        print('{}有{}条相关商品'.format(self.kw,len(self.shop_ip_list)))

    def get_shop_id(self,html):
        '''获取商品详情页的url'''
        contents = html.xpath('//li[@class="gl-item"]/@data-sku')
        for content in contents:
            self.shop_ip_list.append(int(content))

    def get_comment_page(self):
        '''获取评论的页数'''
        for shopid in self.shop_ip_list:
            self.headers['Referer'] = 'https://item.jd.com/{}.html#comment'.format(shopid)
            url = self.url.format(random.choice(range(100,99999)),shopid,0)
            response = self.session.get(url,headers=self.headers,proxies=self.proxies,verify=False).text
            try:
                json_data = re.findall(r'fetchJSON_comment98vv\d+\((.*)\)', response)[0]
            except Exception as e:
                print('{}商品提取错误！'.format(shopid))
            else:
                contents = json.loads(json_data)
                pagenum = contents.get('maxPage', 0)
                self.comment(pagenum,shopid)

    def comment(self,pagenum,shopid):
        page = 0
        while page < pagenum:
            self.headers['Referer'] = 'https://item.jd.com/{}.html#comment'.format(shopid)
            url = self.url.format(random.choice(range(100, 99999)), shopid, page)
            response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
            try:
                json_data = re.findall(r'fetchJSON_comment98vv\d+\((.*)\)', response)[0]
            except Exception as e:
                print('{}商品第{}页评论提取错误！'.format(shopid, page+1))
            else:
                contents = json.loads(json_data)
                for content in contents.get('comments'):
                    item = {}
                    item['shop_id'] = shopid   # 商品ID
                    item['shop'] = content.get('referenceName', '')   # 商品名称
                    item['color'] = content.get('productColor', '')   # 商品颜色
                    item['size'] = content.get('productSize', '')   # 商品大小
                    item['user_id'] = content.get('id', '')   # 用户ID
                    item['nickname'] = content.get('nickname', '')   # 用户昵称
                    item['user_image'] = content.get('userImage', '')   # 用户头像
                    item['comment_time'] = content.get('creationTime', '')   # 评论时间
                    item['content'] = content.get('content', '')   # 评论内容
                    item['shopping_time'] = content.get('referenceTime', '')   # 购买时间
                    item['good'] = content.get('usefulVoteCount', '')   # 点赞数量
                    item['score'] = content.get('score', '')   # 评分
                    item['reply_count'] = content.get('replyCount', '')   # 回复数量
                    item['user_level'] = content.get('userLevelName', '')   # 用户会员等级
                    item['user_client'] = content.get('userClientShow', '')   # 用户客户端

                    print(item)
                    self.save_comment(item)

                print('{}商品第{}页评论提取完成！'.format(shopid, page+1))

            finally:
                page += 1
                time.sleep(3)

        print('{}商品评论提取完成！'.format(shopid))

    def save_comment(self,item):
        '''保存数据'''
        self.cur.execute(
            """insert into jd_comment (shop_id,shop,shop_color,shop_size,user_id,nickname,user_image,comment_time,content,shopping_time,good,score,reply_count,user_level,user_client) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['shop_id'],
                item['shop'],
                item['color'],
                item['size'],
                item['user_id'],
                item['nickname'],
                item['user_image'],
                item['comment_time'],
                item['content'],
                item['shopping_time'],
                item['good'],
                item['score'],
                item['reply_count'],
                item['user_level'],
                item['user_client'],
            ))
        self.connect.commit()

    def main(self):
        self.get_page_html()
        self.get_comment_page()


if __name__ == '__main__':

    urllib3.disable_warnings()

    keyword = input('请输入商品名称：')
    jd = JingDong(keyword)
    jd.main()


