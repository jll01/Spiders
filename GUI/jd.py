import requests
import re
import time
import json
import urllib3
import pymysql
import random
import math

from urllib import parse
from lxml import etree
from threading import Thread,Lock


urllib3.disable_warnings()


class JD(object):
    def __init__(self, kw,thnum):
        # 前30页url
        self.prv_url = 'https://search.jd.com/Search?'
        # 后30页url
        self.after_url = 'https://search.jd.com/s_new.php?'
        # 评论url
        self.comment_url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv{}&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'
        # 关键词
        self.kw = kw
        self.thnum = int(thnum)
        self.page_num = 1
        self.session = requests.session()
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
        ]
        # 商品信息
        self.headers = {
            'User-Agent': random.choice(self.user_agent),
        }
        # 评论
        self.comment_headers = {
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
        # 数据库连接
        self.connect = pymysql.connect(host='',port=0,user='',passwd='',db='')
        self.cur = self.connect.cursor()
        # 存储已经获取到的商品的id，避免重复爬取数据
        self.save_shop_id = []

        self.lock = Lock()

    def join_list(self, res):
        '''|拼接获取到的列表中的数据并去掉空格'''
        if len(res) != 0:
            result = '|'.join(res).strip()
        else:
            result = ''.join(res).strip()
        return result

    def join_null(self,res):
        '''判断并拼接获取到的列表中的数据并去掉空格'''
        if len(res) != 0:
            result = ''.join(res).strip()
        else:
            result = ''
        return result

    def get_shop_page_num(self):
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

    def get_price(self,url):
        '''提取商品的价格'''
        try:
            id = re.match(r'.*?(\d+)\.html', url).group(1)
            price_url = 'https://p.3.cn/prices/mgets?callback=jQuery2414702&type=1&area=1&pdtk=&pduid=15282860256122085625433&pdpin=&pin=null&pdbp=0&skuIds=J_{}'.format(id)
            price = requests.get(price_url,headers=self.headers,verify=False).text
            price_json = json.loads(re.match(r'jQuery2414702\(\[(.*)\]\)', price).group(1))
            return float(price_json.get('p', 0))
        except Exception as e:
            return 0

    def get_page_html(self,page):
        '''只获取页面html'''
        # page = int(self.get_shop_page_num())
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
            response = requests.get(p_url, headers=self.headers, verify=False).text.encode(encoding='utf-8', errors='ignore')
            html = etree.HTML(response)
            self.get_detail_url(html)

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
                # 's': '27',
                'scrolling': 'y',
                'log_id': round(time.time(), 5),
            }
            af_url = self.after_url + parse.urlencode(af_params)
            af_response = requests.get(af_url, headers=headers, verify=False).text.encode(encoding='utf-8', errors='ignore')
            af_html = etree.HTML(af_response)
            self.get_detail_url(af_html)

            print('第{}页下载完成！'.format(num))
            num += 1

            if self.page_num < page*2-1:
                self.page_num += 2
                time.sleep(2)
            else:
                break

    def get_detail_url(self,html):
        '''获取商品详情页的url'''
        contents = html.xpath('//li[@class="gl-item"]')
        # 创建thnum个线程来执行
        for i in range(math.ceil(len(contents)/self.thnum)):
            # 将线程存储
            thread_count = []
            for content in contents[i*self.thnum:(i+1)*self.thnum]:
                try:
                    url = content.xpath('.//div[@class="p-img"]/a/@href')[0]
                    shop_id= int(content.xpath('./@data-sku')[0])
                    if shop_id not in self.save_shop_id:
                        self.save_shop_id.append(shop_id)
                        t = Thread(target=self.get_shop_detail_info, args=(url, shop_id))
                        thread_count.append(t)
                        t.start()
                    else:
                        print('{}商品已经存在！'.format(shop_id))
                except Exception as e:
                    print('一条详情页面链接提取错误！')

            for item in thread_count:
                item.join()

    def get_shop_detail_info(self,detail_url,shop_id):
        '''获取商品的详情信息'''
        url = 'https://' + detail_url.split('//')[1]
        con = requests.get(url,headers=self.headers,verify=False).text.encode(encoding='gbk', errors='ignore')
        content = etree.HTML(con)
        item = {}
        # 爬取时间
        item['spider_date'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        # 商品ID
        item['shop_id'] = shop_id
        # 店铺名称
        item['store_name'] = self.join_null(content.xpath('//div[@class="w"]//div[@class="item"]/div[@class="name"]/a/@title'))
        # 商品
        item['shop'] = self.join_null(content.xpath('//div[@class="w"]//div[@class="itemInfo-wrap"]/div[@class="sku-name"]/text()'))
        # 链接
        item['url'] = url
        # 价格
        item['price'] = self.get_price(url)
        # 品牌
        item['brand'] = self.join_null(content.xpath('//ul[@id="parameter-brand"]/li/a/text()'))

        comment = self.get_comment_info(shop_id)
        # 评论总数
        item['comment_count'] = comment[0]
        # 好评率
        item['good_rate'] = comment[1]
        # 差评率
        item['poor_rate'] = comment[2]
        # 选择的颜色
        item['select_color'] = self.join_list(content.xpath('//div[@class="summary p-choose-wrap"]//div[@id="choose-attr-1"]/div[@class="dd"]/div/@data-value'))
        # 选择的大小
        item['select_size'] = self.join_list(content.xpath('//div[@class="summary p-choose-wrap"]//div[@id="choose-attr-2"]/div[@class="dd"]/div/@data-value'))
        # 效果图片
        item['image'] = self.join_list(content.xpath('//div[@id="spec-list"]/ul/li/img/@src'))

        self.save_con(item)
        print(item)
        # self.get_comment(comment[3], shop_id,item['shop'])

    def get_comment_info(self,shopid):
        '''获取评论的页数、数量、好评率、差评率'''
        self.comment_headers['Referer'] = 'https://item.jd.com/{}.html#comment'.format(shopid)
        url = self.comment_url.format(random.choice(range(100,99999)),shopid,0)
        response = self.session.get(url,headers=self.comment_headers,proxies=self.proxies,verify=False).text
        try:
            json_data = re.findall(r'fetchJSON_comment98vv\d+\((.*)\)', response)[0]
        except Exception as e:
            print('{}商品提取错误！'.format(shopid))
            about_comment = {'goodRate': 1, 'poorRate': 0, 'commentCount': 0}
            good_rate = about_comment.get('goodRate', 1)
            poor_ate = about_comment.get('poorRate', 0)
            comment_count = about_comment.get('commentCount', 0)
            return (comment_count, good_rate, poor_ate, 1)
        else:
            contents = json.loads(json_data)
            pagenum = contents.get('maxPage', 0)
            about_comment = contents.get('productCommentSummary')
            if len(about_comment) == 0:
                about_comment = {'goodRate':1,'poorRate':0,'commentCount':0}

            good_rate = about_comment.get('goodRate',1)
            poor_ate = about_comment.get('poorRate',0)
            comment_count = about_comment.get('commentCount',0)

            return (comment_count,good_rate,poor_ate,pagenum)

    def get_comment(self,pagenum,shopid,shop):
        '''获取商品评论'''
        page = 0
        # 只获取前十页
        if pagenum > 5:
            num = 5
        else:
            num = pagenum
        while page < num:
            self.comment_headers['Referer'] = 'https://item.jd.com/{}.html#comment'.format(shopid)
            url = self.comment_url.format(random.choice(range(100, 99999)), shopid, page)
            response = self.session.get(url, headers=self.comment_headers, proxies=self.proxies, verify=False).text
            try:
                json_data = re.findall(r'fetchJSON_comment98vv\d+\((.*)\)', response)[0]
            except Exception as e:
                print('{}商品第{}页评论提取错误！'.format(shop, page+1))
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

                print('{}商品第{}页评论提取完成！'.format(shop, page+1))

            finally:
                page += 1
                time.sleep(random.choice(range(3,6)))

        print('{}商品评论提取完成！'.format(shop))
        print()

    def save_con(self,item):
        '''保存数据'''
        self.lock.acquire()
        self.cur.execute(
            """insert into jd_shop (spider_date,shop_id,store_name,shop,url,price,brand,comment_count,good_rate,poor_rate,select_color,select_size,image) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['spider_date'],
                item['shop_id'],
                item['store_name'],
                item['shop'],
                item['url'],
                item['price'],
                item['brand'],
                item['comment_count'],
                item['good_rate'],
                item['poor_rate'],
                item['select_color'],
                item['select_size'],
                item['image'],
            ))
        self.connect.commit()
        self.lock.release()

    def save_comment(self,item):
        '''保存数据'''
        self.lock.acquire()
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
        self.lock.release()

    def get_data_from_mysql(self):
        '''从数据库读取已经获取的商品id'''
        self.cur.execute('select shop_id from jd_shop')
        res = self.cur.fetchall()

        for shopid in res:
            self.save_shop_id.append(shopid[0])

    # def main(self):
    #     self.get_data_from_mysql()
    #     self.get_page_html()


# if __name__ == '__main__':
#     urllib3.disable_warnings()

    # keyword = input('请输入商品名称：')
    # th_num = input('请输入多少个线程进行爬取信息：')
    #
    # jd = JD(keyword,th_num)
    # jd.main()

