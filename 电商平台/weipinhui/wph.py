#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   wph.py
# @Time    :   2019/8/3 11:17
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import json
import time
import re
import random
import urllib3
import pymysql
import math

from threading import Thread, Lock


class WeiPinHui(object):
    def __init__(self,keyword,thnum):
        # 线程数量
        self.thnum = thnum
        # 线程锁
        self.lock = Lock()
        self.keyword = keyword
        # user-agent池
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        ]
        self.headers = {
            'User-Agent': random.choice(self.user_agent),
        }
        # IP代理
        self.ip = [
            # '117.191.11.111:8080',
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
            '35.183.111.234:80',
            '144.217.229.157:1080',
            '39.137.69.7:80',
            '39.137.69.7:8080',
            '39.137.69.10:8080'
        ]
        self.proxies = {
            'http': random.choice(self.ip),
        }
        self.session = requests.session()
        self.page = 1
        # 搜索url
        self.search_url = 'https://category.vip.com/suggest.php?keyword={}&page={}&count=50&suggestType=brand#catPerPos'
        # 详细url
        self.info_url = 'https://detail.vip.com/v2/mapi?_path=rest%2Fshop%2Fgoods%2FvendorSkuList%2Fv3&mid={}&brandid={}'
        # 评论url
        self.comment_url = 'https://detail.vip.com/v2/mapi?_path=rest%2Fcontent%2Freputation%2FqueryBySpuId&spuId={}&brandId={}&page={}&pageSize=10'
        # 评论数量
        self.count_url= 'https://detail.vip.com/v2/mapi?_path=rest%2Fcontent%2Freputation%2FgetCountBySpuId&spuId={}&brandId={}'
        # 获取满意度
        self.degree_url = 'https://mapi.vip.com/vips-mobile/rest/ugc/reputation/getSpuIdNlpKeywordV2_for_pc?api_key=70f71280d5d547b2a7bb370a529aeea1&spuId={}'
        # 数据库连接
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()
        # 存储已经获取到信息的商品id
        self.shop_id= []
        # 会员等级
        self.vip = {'D1': '银卡会员', 'D2': '金卡会员', 'D3': '白金卡会员'}

    def get_page_num(self):
        '''获取商品页数'''
        response = requests.get(self.search_url.format(self.keyword,self.page),headers=self.headers,proxies=self.proxies,verify=False).text
        try:
            json_data = re.findall(r"\$\.Var\.set\('suggestMerchandiseList', (.*)\);",response)[0]
            page= json.loads(json_data)
            page_count = page.get("pageCount",0)
        except Exception as e:
            print('出错了!')
            page_count = 0

        return page_count

    def get_id(self):
        '''获取商品id、品牌id'''
        pagenum = self.get_page_num()
        print('{}商品总共有{}页'.format(self.keyword,pagenum))
        while self.page <= pagenum:
            url = self.search_url.format(self.keyword, self.page)
            response = self.session.get(url, headers=self.headers,proxies=self.proxies, verify=False).text
            try:
                data = re.findall(r"\$\.Var\.set\('suggestMerchandiseList', (.*)\);", response)[0]
                json_data = json.loads(data)
                contents = json_data.get('products')
                for i in range(math.ceil(len(contents) / self.thnum)):
                    # 将线程存储
                    thread_count = []
                    for content in contents[i*self.thnum:(i+1)*self.thnum]:
                        item = {}
                        # 商品id
                        item['product_id'] = self.str2num(content.get('product_id'))

                        if item['product_id'] not in self.shop_id:
                            # 爬取时间
                            item['spider_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            # 品牌id
                            item['brand_id'] = self.str2num(content.get('brand_id'))
                            # 品牌名
                            item['brand_name'] = content.get('brand_show_name')
                            # 商品名称
                            item['product_name'] = content.get('product_name')
                            # spuID
                            item['spuid'] = self.str2num(content.get('v_spu_id'))

                            self.shop_id.append(item['product_id'])
                            t = Thread(target=self.get_detail_info, args=(item,))
                            thread_count.append(t)
                            t.start()
                        else:
                            print('{}商品已经存在！'.format(item['product_id']))

                    for tname in thread_count:
                        tname.join()

                    time.sleep(2)
            finally:
                print('{}商品第{}页提取完成！'.format(self.keyword,self.page))
                print('*' * 100)
                self.page += 1
                # time.sleep(3)

    def get_detail_info(self,item):
        '''获取商品详细内容'''
        url = self.info_url.format(item['product_id'], item['brand_id'])
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        try:
            data = json.loads(response).get('data')
            infos = data.get('saleProps')
            item['url'] = 'https://detail.vip.com/detail-{}-{}.html'.format(item['brand_id'],item['product_id'])
            # 商品规格、大小
            attr = self.get_shop_attribute(infos)
            item['spec'] = attr[0]
            # 商品颜色
            item['color'] = attr[1]
            # 获取价格和效果图片
            prices_image = data.get('product_price_range_mapping').get(str(item['product_id']))
            # 打折后价格
            item['salePrice'] = self.str2num(prices_image.get('priceView').get('salePrice').get('salePrice'))
            # 打折前
            item['saleMarketPrice'] = self.str2num(prices_image.get('priceView').get('salePrice').get('saleMarketPrice'))
            # 打折数
            item['saleDiscount'] = prices_image.get('priceView').get('salePrice').get('saleDiscount')
            # 活动价格类型 唯品价、快枪价等
            item['salePriceTips'] = prices_image.get('priceView').get('salePrice').get('salePriceTips')
            # 评论数量
            item['comment_count'] = self.get_comment_count(item['spuid'],item['brand_id'])
            # 满意度
            item['degree_rate'] = self.get_degree(item['spuid'])

            stock = data.get('productSaledStock','')
            if len(stock) != 0:
                item['saleDesc'] = stock.get(str(item['product_id'])).get('saleDesc', '已抢购100%')
            else:
                item['saleDesc'] = ''

            # 效果图片
            item['image'] = 'http://a.vpimg3.com' + self.join_null(prices_image.get('smallImage'))

            print(item)
            self.save_info(item)

        except Exception as e:
            print('提取{}商品的时候出错了{}!'.format(item['product_id'],e))
        finally:
            time.sleep(2)
            self.get_comment_info(item['spuid'],item['brand_id'],item['product_id'],item['product_name'])

    def get_comment_info(self,spuid,brandid,productid,shopname):
        '''获取商品评论内容'''
        page = 1
        while True:
            url = self.comment_url.format(spuid, brandid, page)
            response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
            json_data = json.loads(response)
            data = json_data['data']
            # 没有数据的时候data为空
            if len(data) != 0:
                for comment in data:
                    com = {}
                    com['productid'] = productid
                    com['shopname'] = shopname
                    # 用户信息
                    user = comment.get('reputationUser')
                    # 昵称
                    com['authorName'] = user.get('authorName')
                    # 性别
                    gender = user.get('gender')
                    if gender == "FEMALE":
                        com['gender'] = '女'
                    else:
                        com['gender'] = '男'
                    # 评论时间
                    comment_time = comment.get('reputation').get('postTime')
                    com['comment_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment_time / 1000)))
                    # 等级
                    vip = user.get('memberLvl')
                    com['vip'] = self.vip.get(vip,'')
                    # 内容
                    com['content'] = self.join_null(comment.get('reputation').get('content'))

                    # 身材信息
                    com['stature'] = user.get('stature','')

                    print(com)
                    self.save_comment(com)
                    # time.sleep(0.2)
            else:
                print('{}商品评论内容提取完成'.format(shopname))
                break

            print('{}商品第{}页下载完成！'.format(shopname,page))
            time.sleep(3)
            # 提取每个商品评论内容的前5页
            if page < 5:
                page += 1
            else:
                break

    def get_shop_attribute(self,infos):
        '''获取商品的规格、大小和亚瑟'''
        spec = []
        color = []
        for info in infos[0].get('values'):
            spec.append(info.get('name'))

        for info in infos[1].get('values'):
            color.append(info.get('name'))

        return (self.join_list(spec),self.join_list(color))

    def get_comment_count(self,spuid,brandid):
        url = self.count_url.format(spuid,brandid)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        return json.loads(response).get('data',0)

    def get_degree(self,spuid):
        url = self.degree_url.format(spuid)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        satisfaction = json.loads(response).get('data','')
        if len(satisfaction) != 0:
            return eval(satisfaction.get('satisfaction', '100'))/100
        else:
            return 1

    def join_list(self,res):
        '''拼接列表内容'''
        if len(res) != 0:
            return '|'.join(res).strip().replace(' ','')
        else:
            return ''.join(res).strip()

    def join_null(self,res):
        '''拼接列表内容并判断是否为空'''
        return ''.join(res).strip()

    def str2num(self,res):
        '''将字符串(数字)原格式返回'''
        return eval(res)

    def save_info(self,item):
        '''保存商品信息'''
        self.lock.acquire()
        self.cur.execute(
            """insert into wph_shop (spider_time,url,brand_id,brand_name,product_id,product_name,spuid,spec,color,salePrice,saleMarketPrice,saleDiscount,salePriceTips,saleDesc,comment_count,degree_rate,image) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['spider_time'],
                item['url'],
                item['brand_id'],
                item['brand_name'],
                item['product_id'],
                item['product_name'],
                item['spuid'],
                item['spec'],
                item['color'],
                item['salePrice'],
                item['saleMarketPrice'],
                item['saleDiscount'],
                item['salePriceTips'],
                item['saleDesc'],
                item['comment_count'],
                item['degree_rate'],
                item['image'],
            ))
        self.connect.commit()
        self.lock.release()

    def save_comment(self,item):
        '''保存评论内容'''
        self.lock.acquire()
        self.cur.execute(
            """insert into wph_comment (productid,shopname,authorName,gender,comment_time,content,vip,stature) values (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['productid'],
                item['shopname'],
                item['authorName'],
                item['gender'],
                item['comment_time'],
                item['content'],
                item['vip'],
                item['stature'],
            ))
        self.connect.commit()
        self.lock.release()

    def get_data_mysql(self):
        '''从数据库读取已经获取的商品id'''
        self.cur.execute('select product_id from wph_shop')
        res = self.cur.fetchall()

        for shopid in res:
            self.shop_id.append(shopid[0])

    def main(self):
        self.get_data_mysql()
        self.get_id()
        # self.get_detail_info()

if __name__ == '__main__':
    urllib3.disable_warnings()

    keyword = input('请输入要查找的商品：')
    thnum = int(input('请输入开启的线程数：'))
    wph = WeiPinHui(keyword,thnum)
    wph.main()
