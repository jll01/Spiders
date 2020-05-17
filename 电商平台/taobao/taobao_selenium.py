#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   taobao.py
# @Time    :   2020/5/7 10:13
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import re
import time
import urllib3
import pymysql
import random

from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class TaoBao(object):
    '''淘宝商品信息（名称，价格，销量，人气，每个商品爬取前三页的评论内容），淘宝不允许xpath，通过正则表达式进行提取'''
    def __init__(self,keyword):
        # 关键词
        self.keyword = keyword
        self.cookies = {}
        # cookie池
        self.cookie = [
            'thw=cn; t=30912a0211d2f7c4b616585bc4825060; hng=CN%7Czh-CN%7CCNY%7C156; enc=pzdR76EQ9XgSRGR82Xq45tmJruRFWu0FouJ8kQAkE3nawWt6z1uotCujQi0PcMIZI%2FB7iYyg4rl8rsxLX1xJSA%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; _m_h5_tk=bd1525710e4afb9c577d8a990f3353b7_1564926869087; _m_h5_tk_enc=5a6d2edb8c06b13c3c5e8c0a0e6dd566; cookie2=166f3000b9672c536c59566b63e90b79; _tb_token_=eeb3a3bb33a33; _uab_collina=156492382396750161615565; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; swfstore=200907; mt=ci=0_0; cna=353FFR0e5FsCAXa3WpLq0giz; v=0; x5sec=7b227365617263686170703b32223a223464386535366432633737383636646133303535303466613238643738363734434f572b6d2b6f46454b2b367a35364f334b625954526f504d6a49774d7a41334d6a597a4e6a4d7a4d447378227d; JSESSIONID=8405DFCA73B5B3B1C30D44ED9D1A4A79; isg=BEVFs3FGtIJs1ZBax07XR-RvVIG_qvjxG33nnEeq5nyL3mdQDlZSZIH86EKNnhFM; l=cBSHVLunqYl65142BOfZCuI8LPbt5IRbzsPzw4OG4ICPOb5e5cvcWZFPC28wCnGVK6uJJ3oWYJ1uB0L5yyCqJxpsw3k_J_f..',
            # 'thw=cn; t=4a67cf0f54b38a06b12baa6d7011ac01; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; mt=ci=0_0; cna=353FFR0e5FsCAXa3WpLq0giz; hng=CN%7Czh-CN%7CCNY%7C156; v=0; cookie2=1188c00dd90500ec2caf188256b95566; _tb_token_=555f6ebe1f33b; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; JSESSIONID=8D4A142105251AA3BD42FD981CC4D589; uc1=cookie14=UoTaHP3Aq5rlzQ%3D%3D; isg=BC0t8WQ9DM36--hecDw_dwcBPMlnImA0s3X_RG8wZkQU5kmYNNvhLE_g0fql0nkU; l=cBTFlrMmqbmpLQB3BOfgCuI8Ls7OmQAfCfVzw4OGjICP9mCwkrwcWZFXDALeCnhVp6UM83oWYJ1uBeYBqtftHxoD2j-la',
            # 'thw=cn; t=4a67cf0f54b38a06b12baa6d7011ac01; enc=z0TfWvQ9HWXGg%2FRoa2MY2HYj2UfgrfgniIYK%2FEv2r%2FGt32csHyi8iBOmGabkyql62Uuf9%2BYrgcukKLieAnE%2FjA%3D%3D; mt=ci=0_0; cna=353FFR0e5FsCAXa3WpLq0giz; hng=CN%7Czh-CN%7CCNY%7C156; v=0; cookie2=1188c00dd90500ec2caf188256b95566; _tb_token_=555f6ebe1f33b; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; uc1=cookie14=UoTaHP3Aq5rlzQ%3D%3D; JSESSIONID=D1451FA603364663FBC5F784EEC1FCC0; isg=BLW1cbogBDUCUGD2CFQHX08pxDGvmmgsay137DfaIix7DtQA24PHFIzMWZKdeoH8; l=cBTFlrMmqbmpL_gtBOCwSuI8Ls79YIR2muPRwC0Xi_5Q49L6OfbOkStYshp6DjWd9SJ640tUd_29-etliOHx3mx-g3fP.',
        ]
        # user-agent池
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        ]
        self.headers = {
            'cookie': random.choice(self.cookie),
            'referer': 'https://s.taobao.com/search',
            'user-agent': random.choice(self.user_agent),
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
        # 获取当前的年月日
        self.date = time.strftime('%Y%m%d',time.localtime(time.time()))
        # 初始页码
        self.page = 0
        # 淘宝搜索url
        self.page_url = 'https://s.taobao.com/search?q={keyword}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_{date}&ie=utf8&s={page}'
        # 开启一个session会话
        self.session = requests.session()
        # 将cookiesJar赋值给会话
        self.session.cookies = self.read_cookies()
        # mysql数据库
        self.connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cursor = self.connect.cursor()
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_drive = r'D:\soft\Chrome\chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chrome_drive, options=chrome_options)
        self.count = 1  # 最多识别6次

    def read_cookies(self):
        # 读取cookies， 登陆的cookie
        cookies_txt = '_uab_collina=156463515877914067033822; thw=cn; t=30912a0211d2f7c4b616585bc4825060; cookie2=12c4a1f9cf81ee5cd2bc4dcb857b9549; _tb_token_=e1f17347053eb; XSRF-TOKEN=cdc2a6c2-7b70-4783-9f74-bf21b75aff9f; hng=CN%7Czh-CN%7CCNY%7C156; enc=pzdR76EQ9XgSRGR82Xq45tmJruRFWu0FouJ8kQAkE3nawWt6z1uotCujQi0PcMIZI%2FB7iYyg4rl8rsxLX1xJSA%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; whl=-1%260%260%261564648112426; mt=ci=0_0; cna=353FFR0e5FsCAXa3WpLq0giz; v=0; l=cBSHVLunqYl65IkzKOfwIuI8Ls7TiIRb8sPzw4OGjICP9gXy53ZGWZF2cUt2CnGVL68k-3oWYJ1uBPYowyUBh9KwNBQ7XPQl.; isg=BIWF7DRkdEZQ3lAah44XByQvlMF_6ji82z0nXIfqyLzKHqeQTZYLpRX8KAJNXlGM'
        for cookie in cookies_txt.split(';'):
            name, value = cookie.strip().split('=', 1)  # 用=号分割，分割1次
            self.cookies[name] = value  # 为字典cookies添加内容
        # 将字典转为CookieJar：
        cookiesJar = requests.utils.cookiejar_from_dict(self.cookies, cookiejar=None, overwrite=True)
        return cookiesJar

    def get_page_num(self):
        '''获取输入的商品的总页数'''
        url = self.page_url.format(keyword=self.keyword,date=self.date,page=self.page)
        response = self.session.get(url,headers=self.headers,proxies=self.proxies,verify=False).text
        try:
            pagenum = re.findall(r'"totalPage":(\d+)', response)[0]
        except Exception as e:
            return 0
        else:
            return int(pagenum)

    def get_shop_info(self):
        '''淘宝商品爬虫主程序，通过正则表达式获取搜索页面中商品的信息'''
        pagenum = self.get_page_num()
        if pagenum != 0:
            print('商品{}总共有{}页'.format(self.keyword,pagenum))
            for page in range(0,pagenum):
                url = self.page_url.format(keyword=self.keyword,date=self.date,page=page*44)
                response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False,timeout=5).text
                # 商品id
                nid = re.findall(r'\"nid\"\:\"(.*?)\"', response)
                # 店铺id
                user_id = re.findall(r'\"user_id\"\:\"(.*?)\"', response)
                # 详细链接
                detail_url= re.findall(r'\"detail_url\"\:\"(.*?)\"',response)
                # 商品名
                raw_title = re.findall(r'\"raw_title\"\:\"(.*?)\"', response)
                # 店名
                nick = re.findall(r'\"nick\"\:\"(.*?)\"', response)
                # 价格
                view_price = re.findall(r'\"view_price\"\:\"(.*?)\"', response)
                # 付款人数
                view_sales = re.findall(r'\"view_sales\"\:\"(.*?)\"', response)
                # 地址
                item_loc = re.findall(r'\"item_loc\"\:\"(.*?)\"', response)

                infos = zip(nid,user_id,detail_url,raw_title,nick,view_price,view_sales,item_loc)
                for info in infos:
                    item = {}
                    # 爬取时间
                    item['spider_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    # 商品id
                    item['shop_id'] = self.str2num(info[0])
                    # 商品详情页url
                    item['detail_url'] = info[2].encode('latin-1').decode('unicode_escape')
                    # 商品名
                    item['shop'] = info[3]
                    # 店名
                    item['store_name'] = info[4]
                    # 店铺id
                    item['user_id'] = self.str2num(info[1])
                    # spuid
                    item['spuid'] = self.str2num(self.get_spuID(item['detail_url']))
                    # 价格
                    item['price'] = self.str2num(info[5])
                    # 付款人数
                    item['pay_count'] = info[6]
                    # 地址
                    item['addr'] = info[7]

                    sales = self.get_sale(item['shop_id'])
                    # 月销量
                    item['month_sale'] = sales[0]
                    # 库存
                    item['stock'] = sales[1]
                    # 评论人数
                    item['comment_count'] = self.get_comment_count(item['shop_id'])
                    # 商品收藏数量（人气）
                    item['popularity'] = self.get_popularity(item['shop_id'])

                    detail_info = self.get_detail_info(item['shop_id'])
                    # 描述相符
                    item['description'] = detail_info[0]
                    # 服务态度
                    item['service'] = detail_info[1]
                    # 物流速度
                    item['delivery'] = detail_info[2]
                    # 图片
                    item['image'] = detail_info[3]
                    # 评论标签
                    item['comment_tag'] = self.get_comment_tag(item['shop_id'])
                    # 将商品信息保存到数据库
                    self.save_shop(item)

                    print(item)
                    if item['comment_count'] != 0:
                        self.get_comment(item['shop_id'],item['shop'])
                    else:
                        print('{}商品暂时没有评论内容！'.format(item['shop']))

                print('第{}页商品信息提取完成！'.format(page+1))
                time.sleep(random.choice(range(3,6)))
        else:
            print('未找到商品{},请稍后再试！'.format(self.keyword))

    def get_spuID(self,detail_url):
        headers = {
            'user-agent': random.choice(self.user_agent),
            'authority': 'detail.tmall.com',
            'method': 'GET',
            'path': self.join_null(re.findall(r'(/item.*)',detail_url)),
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'cna=353FFR0e5FsCAXa3WpLq0giz; lid=%E6%98%8E%E5%A4%A9%E4%B8%89%E5%8D%81%E4%BA%8C%E5%8F%B7; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; OZ_1U_2061=vid=vd4005c2246af6.0&ctime=1564477834&ltime=1564477830; hng=CN%7Czh-CN%7CCNY%7C156; enc=pzdR76EQ9XgSRGR82Xq45tmJruRFWu0FouJ8kQAkE3nawWt6z1uotCujQi0PcMIZI%2FB7iYyg4rl8rsxLX1xJSA%3D%3D; cq=ccp%3D1; t=30912a0211d2f7c4b616585bc4825060; uc4=nk4=0%40oh%2FcWHnT71%2F07B7UBMCXEvZjN8TJYeA%3D&id4=0%40U2grEhAnq3dBcT5Sw52UMGhXeNOytWiV; _tb_token_=eeb3a3bb33a33; cookie2=166f3000b9672c536c59566b63e90b79; _m_h5_tk=67adc976d4b69948198958cc7607c128_1564930648104; _m_h5_tk_enc=5c3e0362d25e5efac8bdc8bd8f97a76d; swfstore=232995; pnm_cku822=098%23E1hvypvUvbpvUvCkvvvvvjiPRFFyAjYERszOQj3mPmPp0jDWPFMvgjtUnLSwsjE8iQhvCvvv9UUtvpvhvvvvv8yCvv9vvUv0jnSX6OyCvvOUvvVva6RtvpvIvvvvvhCvvvvvvvWvphvUoQvvvQCvpvACvvv2vhCv2RvvvvWvphvWgvyCvhQpVDGvCsBlYWoQrEttoY2Z%2BnezrmphQRAn3feAOHPIAXcBKFyK2ixrAj7J%2B3%2BFafmxfBAKNZ0QD7zWditkPrcvAWvXbFZHAW2UwfIOvphvC9vhvvCvpvGCvvpvvPMM; l=cBSl_5s7qPUMAXYbBOCN5uI8LPbTQIRfguPRwCcXi_5ZtsY1lKQOk7WCTUv6cjWdOsYB40tUd_v9-etknTB_MO5P97RN.; isg=BJOT1qrSyvwKD4bznORERmiQIhd94CZvuRdRSkWw9LLoxLNmzR33WgYG-nQP5H8C',
            'pragma': 'no-cache',
            'upgrade-insecure-requests': '1',
        }
        url = 'https://' + detail_url.split('//')[1]
        response = self.session.get(url, headers=headers, proxies=self.proxies, verify=False).text
        try:
            spuid = re.findall(r'\"spuId\":(\d+)', response)[0]
        except Exception as e:
            spuid = '0'
        return spuid

    def get_comment(self,shop_id,shop_name):
        '''获取每个商品评论内容'''
        comment_url = 'https://detail.tmall.com/item.htm?id={}&ns=1&abbucket=17&on_comment=1'.format(shop_id)
        self.driver.get(comment_url)
        page = 1
        num = random.randint(3,5)
        while page <= num:
            time.sleep(random.choice(range(3, 5)))
            response = etree.HTML(self.driver.page_source)
            judje= response.xpath('//iframe[contains(@src,"rate.tmall.com:443")]')
            if len(judje) == 0:
                contents = response.xpath('//div[@class="tm-rate"]/div[@class="rate-grid"]//tbody/tr')
                if len(contents) != 0:
                    for content in contents:
                        item = {}
                        # 商品id
                        item['shop_id'] = shop_id
                        # 商品名称
                        item['shop'] = shop_name
                        # 评论内容
                        comment = self.join_null(content.xpath(
                            './td[@class="tm-col-master"]/div[@class="tm-rate-content"]/div[@class="tm-rate-fulltxt"]/text()'))
                        if len(comment) != 0:
                            item['content'] = comment
                        else:
                            item['content'] = self.join_null(content.xpath('./td[@class="tm-col-master"]/div[@class="tm-rate-premiere"]/div[@class="tm-rate-content"]/div[@class="tm-rate-fulltxt"]/text()'))
                        # # 颜色分类
                        # item['color'] = self.join_null(content.xpath('./td[@class="col-meta"]/div[@class="rate-sku"]/p[1]/@title')).split(':')[1]
                        # # 尺寸
                        # item['size'] = self.join_null(content.xpath('./td[@class="col-meta"]/div[@class="rate-sku"]/p[2]/@title')).split(':')[1]

                        # 商品属性
                        classifies = content.xpath('./td[@class="col-meta"]/div[@class="rate-sku"]/p')
                        classify_list = []
                        for classify in classifies:
                            classify_list.append(self.join_null(classify.xpath('./@title')))
                        item['classify'] = self.join_list(classify_list)

                        # 昵称
                        item['nick'] = self.join_nickname(
                            content.xpath('./td[@class="col-author"]/div[@class="rate-user-info"]/text()'))
                        # 会员等级
                        item['vip'] = self.join_null(
                            content.xpath('./td[@class="col-author"]/div[@class="rate-user-grade"]/p/text()'))
                        # 评论日期
                        comment_date = self.join_null(
                            content.xpath('./td[@class="tm-col-master"]/div[@class="tm-rate-date"]/text()'))
                        if len(comment_date) != 0:
                            item['comment_date'] = comment_date
                        else:
                            item['comment_date'] = self.join_null(content.xpath('./td[@class="tm-col-master"]/div[@class="tm-rate-premiere"]/div[@class="tm-rate-tag"]/div[@class="tm-rate-date"]/text()'))

                        print(item)
                        self.save_comment(item)
                    print('----------{}商品第{}页评论提取完成！----------'.format(shop_name,page))

                    try:
                        element = self.driver.find_element_by_link_text('下一页>>')
                        webdriver.ActionChains(self.driver).move_to_element(element).click(element).perform()
                    except:
                        print('{}商品暂时没有更多评论内容！'.format(shop_name))
                        break

                    page += 1

                else:
                    contents2 = response.xpath('//div[@class="tb-revbd"]/ul/li')
                    if len(contents2) != 0:
                        for content2 in contents2:
                            item2 = {}
                            # 商品id
                            item2['shop_id'] = shop_id
                            # 商品名称
                            item2['shop'] = shop_name
                            # 昵称
                            item2['nick'] = self.join_null(content2.xpath('./div[@class="from-whom"]/div/text()'))
                            # 评论内容
                            item2['content'] = self.join_null(content2.xpath('./div[@class="review-details"]/div[contains(@class,"tb-rev-item")][1]/div[contains(@class,"J_KgRate_ReviewContent")]/text()'))
                            # 属性
                            item2['classify'] = self.join_null(content2.xpath('./div[@class="review-details"]/div[contains(@class,"tb-rev-item")][1]/div[@class="tb-r-act-bar"]/div[@class="tb-r-info"]/text()'))
                            # 会员等级
                            item2['vip'] = ''
                            # 评论日期
                            item2['comment_date'] = self.join_null(content2.xpath('./div[@class="review-details"]/div[contains(@class,"tb-rev-item")][1]/div[@class="tb-r-act-bar"]/div[@class="tb-r-info"]/span[@class="tb-r-date"]/text()'))

                            print(item2)
                            self.save_comment(item2)

                        print('----------{}商品第{}页评论提取完成！----------'.format(shop_name, page))

                        try:
                            element = self.driver.find_element_by_xpath('//*[@id="reviews"]/div[@class="kg-rate"]/div[@class="kg-rate-main"]/div[@class="kg-rate-detail"]/div[@class="J_KgRate_Main"]/div[@class="J_KgRate_MainReviews"]/div[2]/div/ul/li[@class="pg-next"]')
                            webdriver.ActionChains(self.driver).move_to_element(element).click(element).perform()
                        except:
                            print('{}商品暂时没有评论内容！'.format(shop_name))
                            break
                        page += 1
            else:
                while True:
                    print('----------第{}次识别----------'.format(self.count))
                    try:
                        iframe = self.driver.find_element_by_xpath('//iframe[contains(@src,"rate.tmall.com:443")]')
                        self.driver.switch_to.frame(iframe)
                        element = self.driver.find_element_by_xpath('//span[@id="nc_1_n1z"]')  # 需要滑动的元素
                        self.main_check_code(element)
                    except Exception as e:
                        pass
                    finally:
                        self.driver.refresh()
                        time.sleep(3)
                        try:
                            iframe1 = self.driver.find_element_by_xpath('//iframe[contains(@src,"rate.tmall.com:443")]')
                        except Exception as e:
                            print('验证成功！')
                            self.count = 0
                            break
                        else:
                            print('第{}次验证失败！'.format(self.count))
                            self.count += 1

    def get_detail_info(self,id):
        '''进入到商品详情页面，通过xpath提取描述相符，快递，服务，效果图片等信息'''
        url = 'https://detail.tmall.com/item.htm?spm=a230r.1.14.6.7ea570e4OTwAN1&id={}&cm_id=140105335569ed55e27b&abbucket=14'.format(id)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False)
        # brandid = response.headers.get('at_brid','')
        html = etree.HTML(response.text)
        info = html.xpath('//div[@id="shop-info"]/div[@class="main-info"]//span/text()')
        # 获取到的值大小不为3（描述，服务，物流），则都赋值为空值
        if len(info) < 3:
            info = ['','','']
        # 描述
        description = self.str2num(info[0])
        # 服务
        service = self.str2num(info[1])
        # 快递
        delivery = self.str2num(info[2])
        # 图片
        image = self.join_list(html.xpath('//ul[@id="J_UlThumb"]/li//img/@src'))

        return (description,service,delivery,image)

    def get_sale(self, id):
        '''获取月销量和库存'''
        url = 'https://mdskip.taobao.com/core/initItemDetail.htm?isUseInventoryCenter=false&cartEnable=true&service3C=false&isApparel=true&isSecKill=false&tmallBuySupport=true&isAreaSell=false&tryBeforeBuy=false&offlineShop=false&itemId={}&showShopProm=false&isPurchaseMallPage=false&itemGmtModified=1564498123000&isRegionLevel=false&household=false&sellerPreview=false&queryMemberRight=true&addressLevel=2&isForbidBuyItem=false&callback=setMdskip&timestamp=1564498134698&isg=cBSl_5s7qPUMAzBYBOfwZuI8Ls7t2CdbzVVzw4OGjICP9R1ymywcWZFxBxY2CnhVK64w-3oWYJ1uB7YeeyIIK72O-_Bkdl5..&isg2=BBUVUOwS5BRb6MC1rm7aGPr6JBEPushMyw2XDJe_aQxo7jHgXWIh9THnubJ9XuHc&ref=https%3A%2F%2Fs.taobao.com%2Fsearch%3Fie%3Dutf8%26initiative_id%3Dstaobaoz_20190730%26stats_click%3Dsearch_radio_all%253A1%26js%3D1%26imgfile%3D%26q%3D%25E5%2586%2585%25E8%25A3%25A4%25E5%25A5%25B3%26suggest%3D0_1%26_input_charset%3Dutf-8%26wq%3D%25E5%2586%2585%25E8%25A3%25A4%26suggest_query%3D%25E5%2586%2585%25E8%25A3%25A4%26source%3Dsuggest'.format(id)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        # 月销量
        sale = self.join_null(re.findall(r'"sellCount":"(.*?)","success"', response)) #re.findall(r'\((.*)\)',s)[0]
        # 库存
        stock = self.str2num(self.join_null(re.findall(r'"icTotalQuantity":(\d+)', response)))

        return (sale,stock)

    def get_comment_tag(self,id):
        '''获取评论标签'''
        url = 'https://rate.tmall.com/listTagClouds.htm?itemId={}&isAll=true&isInner=true&t=1564498513649&groupId=&_ksTS=1564498513649_1660&callback=jsonp1661'.format(id)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        comment_tag = re.findall(r'"tag":"(.*?)"',response)
        return self.join_list(comment_tag)

    def get_comment_count(self,id):
        '''获取累计评价'''
        url = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId={}&spuId=1115341539&sellerId=1939795057&groupId&_ksTS=1564549627992_213&callback=jsonp214'.format(id)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        comment_count = re.findall(r'"rateTotal":(\d+)', response)
        return self.str2num(self.join_null(comment_count))

    def get_popularity(self,id):
        '''商品人气，即收藏数量'''
        url = 'https://count.taobao.com/counter3?_ksTS=1564547061855_261&callback=jsonp262&keys=SM_368_dsr-2177707621,ICCP_1_{}'.format(id)
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, verify=False).text
        popularity = re.findall(r'"ICCP_1_\d+":(\d+)', response)
        return self.str2num(self.join_null(popularity))

    @staticmethod
    def join_null(res):
        '''对传入的列表进行拼接（这儿主要时避免判断列表是否为空）空即返回""'''
        return ''.join(res)

    @staticmethod
    def join_list(res):
        '''主要争对列表中的值代表不同的属性需要区别以便直观'''
        if len(res) != 0:
            return '|'.join(res)
        else:
            return ''.join(res)

    @staticmethod
    def join_nickname(res):
        '''昵称拼接""'''
        if len(res) == 2:
            return  res[0] + '***' + res[1] + '（匿名）'
        else:
            return ''.join(res)

    @staticmethod
    def str2num(res):
        '''传入的值不为空则将字符串转换为数字，原数字类型是什么就返回什么类型的数字'''
        if len(res) != 0:
            return eval(res)
        else:
            return 0

    def save_shop(self,item):
        '''保存商品数据'''
        self.cursor.execute(
            """insert into taobao_shop (spider_time,shop_id,detail_url,shop,store_name,user_id,spuid,price,pay_count,addr,month_sale,stock,comment_count,popularity,description,service,delivery,image,comment_tag) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['spider_time'],
                item['shop_id'],
                item['detail_url'],
                item['shop'],
                item['store_name'],
                item['user_id'],
                item['spuid'],
                item['price'],
                item['pay_count'],
                item['addr'],
                item['month_sale'],
                item['stock'],
                item['comment_count'],
                item['popularity'],
                item['description'],
                item['service'],
                item['delivery'],
                item['image'],
                item['comment_tag'],
             ))
        self.connect.commit()

    def save_comment(self,com):
        '''保存评论数据'''
        self.cursor.execute(
            """insert into taobao_comment (shop_id,shop,comment_date,nick,classify,content,vip) values (%s,%s,%s,%s,%s,%s,%s)""",
            (
                com['shop_id'],
                com['shop'],
                com['comment_date'],
                com['nick'],
                com['classify'],
                com['content'],
                com['vip'],
            ))
        self.connect.commit()

    def get_track(self,distance):
        '''移动轨迹，模仿人的滑动行为，先匀加速后匀减速'''
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        t_a = 0.2
        t1 = 1.5
        t2 = 0.5
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 加速度(计划3秒内完成滑动)
        a1 = 2 * distance / 3
        # 减速度（3秒内完成，公式推导）
        a2 = -6 * distance
        while True:
            if t_a <= t1:
                # 初速度
                v0 = v
                # 0.2秒时间内的位移
                s = v0 * t + 0.5 * a1 * (t ** 2)
                tracks.append(round(s))
                # 下次的初速度
                v = v0 + a1 * t
                # 总用时
                t_a += t
            elif t1 < t_a and t_a <= t1 + t2:
                v0 = a1 * t1
                s = v0 * t + 0.5 * a2 * (t ** 2)
                tracks.append(round(s))
                v = v0 + a2 * t
                t_a += t
            else:
                break

        tracks.append(distance - sum(tracks))
        return tracks

    def main_check_code(self, element):
        """拖动识别验证码"""
        track_list = self.get_track(400)
        print(sum(track_list),track_list)
        print('点击滑动按钮')
        ActionChains(self.driver).click_and_hold(on_element=element).perform()  # 点击鼠标左键，按住不放
        time.sleep(1)
        print('拖动元素')
        for track in track_list:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=random.randint(2,5)).perform()  # 鼠标移动到距离当前位置（x,y）
            time.sleep(0.002)
        # ActionChains(self.driver).move_by_offset(xoffset=random.randint(1,3), yoffset=0).perform()
        print('滑动完成')
        time.sleep(1)
        ActionChains(self.driver).release(on_element=element).perform()
        time.sleep(1)

    def main(self):
        self.get_shop_info()


if __name__ == '__main__':
    # 禁止requests对https请求时出现的警告
    urllib3.disable_warnings()

    keyword = input('请输入商品名称：')
    tb = TaoBao(keyword)
    tb.main()
