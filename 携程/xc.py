import requests
import urllib3
import json
import re
import time
import random
import pymysql


class XieCheng(object):

    def __init__(self, cityname):
        self.page = 1
        self.url = 'https://hotels.ctrip.com/hotel/{}/p{}'
        self.cityid_url = 'https://hotels.ctrip.com/Domestic/Tool/AjaxGetCitySuggestion.aspx'
        self.cityname = cityname
        # IP代理
        ip = [
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
            'http': random.choice(ip),
        }
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        }

        self.session = requests.session()
        # 数据库
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    @staticmethod
    def star(res):
        if len(res) != 0:
            return eval(res[-1])
        else:
            return 0

    @staticmethod
    def str2num(res):
        if len(res) != 0:
            return eval(res)
        else:
            return 0

    @staticmethod
    def get_price(prices):
        pricelist = []
        for price in prices:
            item = {}
            item[price['hotelid']] = price['amount']
            pricelist.append(item)
        return pricelist

    def cityid(self):
        cityids = self.session.get(self.cityid_url, headers=self.headers,proxies=self.proxies).text
        re_data = eval(re.findall(r'suggestion=(.*)',cityids)[0].replace('display','"display"').replace('data','"data"').replace('group','"group"').replace('热门','"热门"').replace('ABCD','"ABCD"').replace('EFGH','"EFGH"').replace('JKLM','"JKLM"').replace('NOPQRS','"NOPQRS"').replace('TUVWX','"TUVWX"').replace('YZ','"YZ"'))
        contents = []
        rm = re_data.get('热门')
        contents.append(rm)
        ad = re_data.get('ABCD')
        contents.append(ad)
        eh = re_data.get('EFGH')
        contents.append(eh)
        jm = re_data.get('JKLM')
        contents.append(jm)
        ns = re_data.get('NOPQRS')
        contents.append(ns)
        tx = re_data.get('TUVWX')
        contents.append(tx)
        yz = re_data.get('YZ')
        contents.append(yz)

        item = {}
        for content in contents:
            for ids in content:
                data = ids['data'].split('|')
                item[ids['display']] = data[0] + data[2]

        with open('cityid.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False))

        return item

    @staticmethod
    def get_id(city_id, name):
        city = eval(city_id)
        flag = 0
        for key,value in city.items():
            if key == name:
                flag = 1
                return value

        if flag == 0:
            return 0

    def save_data(self,item):
        self.cur.execute(
            """insert into xc (hotelid,name,shortName,url,img,address,price,score,dpscore,dpcount,star,stardesc) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['hotelid'],
                item['name'],
                item['shortName'],
                item['url'],
                item['img'],
                item['address'],
                item['price'],
                item['score'],
                item['dpscore'],
                item['dpcount'],
                item['star'],
                item['stardesc'],
            ))
        self.connect.commit()

    def get_page(self, id):
        count = 0
        while True:
            page = self.session.get(self.url.format(id,self.page), headers=self.headers,proxies=self.proxies).text
            try:
                contents = eval(re.findall(r'hotelPositionJSON:\s+(\[.*\])',page)[0])
                prices = eval(re.findall(r"htllist:\s+'(\[.*\])'",page)[0])
                hotelnum = self.str2num(re.findall(r"hotelnum:\s+'(\d+)'",page)[0])
            except Exception as e:
                print('未获取到页面信息，数据提取错误!')
            else:
                pricelist = self.get_price(prices)
                for content in contents:
                    item = {}
                    # 酒店id
                    item['hotelid'] = self.str2num(content.get('id', '0'))
                    # 酒店名称
                    item['name'] = content.get('name', '')
                    # 酒店简称
                    item['shortName'] = content.get('shortName', '')
                    # 详情链接
                    item['url'] = 'https://hotels.ctrip.com' + content.get('url', '')
                    # 酒店效果图
                    item['img'] = content.get('img', '')
                    # 地址
                    item['address'] = content.get('address', '')
                    # 价格
                    for price in pricelist:
                        if str(item['hotelid']) == list(price.keys())[0]:
                            item['price'] = self.str2num(price.get(str(item['hotelid'])))
                    # 评分
                    item['score'] = self.str2num(content.get('score', '0'))
                    # 用户推荐率96%
                    item['dpscore'] = self.str2num(content.get('dpscore', '0'))
                    # 点评客户
                    item['dpcount'] = self.str2num(content.get('dpcount', '0'))
                    # 酒店是几星
                    item['star'] = self.star(content.get('star', '0'))
                    # 酒店类型
                    item['stardesc'] = content.get('stardesc', '')

                    print(item)
                    self.save_data(item)
                    count += 1
                print('共获取{}页数据，总共有{}家酒店'.format(self.page,count))
            finally:
                if count < hotelnum:
                    self.page += 1
                else:
                    break

                time.sleep(random.randint(3,5))

    def main(self):
        with open('cityid.json', 'r', encoding='utf-8') as f:
            city_id = f.read()
        if len(city_id) == 0:
            self.cityid()

        flag = 0
        while True:
            id = self.get_id(city_id,self.cityname)
            if id != 0:
                self.get_page(id)
                break
            else:
                flag += 1
                if flag == 2:
                    print('查找错误！退出程序，请确认城市信息后再使用！')
                    break
                self.cityname = input('查找错误！请重新输入城市名称：')


if __name__ == '__main__':

    urllib3.disable_warnings()

    cityname = input('请输入城市名(北京)：')

    xc = XieCheng(cityname)
    xc.main()
