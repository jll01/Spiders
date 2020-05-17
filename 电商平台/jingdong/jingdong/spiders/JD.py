# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import requests
import urllib3

from jingdong.items import JingdongItem

urllib3.disable_warnings()

class JdSpider(scrapy.Spider):
    name = 'JD'
    allowed_domains = ['search.jd.com']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
    }
    # 前30条信息url
    first_url = 'https://search.jd.com/Search?keyword={key}&enc=utf-8&page={page}'
    # 后30条信息url
    last_url = 'https://search.jd.com/Search?keyword={key}&enc=utf-8&page={page}&qrst=1&rt=1&stop=1&vt=2&wq={wq}&scrolling=y&log_id={time_time}'
    # 关键词，商品名称
    kw = input('请输入商品名称：')
    page = 1

    start_urls = [first_url.format(key=kw,page=page)]

    def parse(self, response):
        # 获取当前商品的总页数
        page = int(self.get_page_num(response))
        for page_num in range(1, page+1):
            first = self.first_url.format(key=self.kw, page=page_num*2-1)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                "referer": first,
            }
            # 获取每一页前30条数据
            yield scrapy.Request(url=first,headers=self.headers,callback=self.get_url,dont_filter=True)
            # 获取后30条数据
            yield scrapy.Request(url=self.last_url.format(key=self.kw,page=2*page_num,wq=self.kw,time_time=round(time.time(),5)),headers=headers,callback=self.get_url,dont_filter=True)

    def get_page_num(self,response):
        '''获取当前商品有多少页'''
        page = response.xpath('//div[@id="J_topPage"]/span/i/text()').get()
        print('{}商品总共有{}页'.format(self.kw,page))
        return page

    def get_url(self,response):
        '''获取商品详情页的url'''
        contents = response.xpath('//div[@id="J_goodsList"]//li[@class="gl-item"]/div[@class="gl-i-wrap"]')
        for content in contents:
            url = content.xpath('./div[@class="p-name p-name-type-2"]/a/@href')
            if len(url) != 0:
                detail_url = url.get()
            else:
                detail_url = content.xpath('.//div[@class="gl-i-tab-content"]//div[@class="p-name p-name-type-2"]/a/@href').get()

            url = 'https://' + detail_url.split('//')[1]

            yield scrapy.Request(url=url,headers=self.headers,callback=self.get_content,dont_filter=True)

    def get_content(self,response):
        '''获取商品的详情信息'''
        item = JingdongItem()
        # 爬取时间
        item['date'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        item['url'] = response.request.url
        item['shop_name'] = self.judje_res(response.xpath('//div[@class="w"]//div[@class="item"]/div[@class="name"]/a/text()').extract())

        title = ''.join(response.xpath('//div[@class="w"]//div[@class="itemInfo-wrap"]/div[@class="sku-name"]/text()').extract())
        item['goods'] = title.strip()

        item['brand'] = self.judje_res(response.xpath('//ul[@id="parameter-brand"]/li/a/text()').extract())
        item['price'] = self.get_price(item['url'])

        comment = self.get_comment(item['url'])
        item['comment_count'] = comment[0]
        item['good_rate'] = comment[1]
        item['poor_rate'] = comment[2]

        item['select_shop'] = self.join_list(response.xpath('//div[@class="summary p-choose-wrap"]//div[@id="choose-attr-1"]/div[@class="dd"]/div/a/i/text()').extract())
        item['image'] = self.join_list(response.xpath('//div[@id="spec-list"]/ul/li/img/@src').extract())
        # 食品才有
        pars = response.xpath('//div[@class="p-parameter"]/ul[2]/li')
        p = {}
        for par in pars:
            detail = par.xpath('./text()').get().split('：')
            p[detail[0]] = detail[1]

        item['weight'] = p.get('商品毛重','不存在')
        item['category'] = p.get('类别','不存在')
        item['sugar'] = p.get('是否含糖','不存在')
        item['fat'] = p.get('脂肪含量','不存在')
        item['addr'] = p.get('商品产地','不存在')

        print(item['url'],item['shop_name'],item['goods'])
        yield item

    def judje_res(self,res):
        '''判断返回的列表是否为空'''
        if len(res) != 0:
            return res[0]
        else:
            return ''

    def get_price(self,url):
        '''提取商品的价格'''
        try:
            id = re.match(r'.*?(\d+)\.html', url).group(1)
            price_url = 'https://p.3.cn/prices/mgets?callback=jQuery24147&a02&type=1rea=1&pdtk=&pduid=15282860256122085625433&pdpin=&pin=null&pdbp=0&skuIds=J_{}'.format(id)
            price = requests.get(price_url,headers=self.headers,verify=False).text
            price_json = json.loads(re.match(r'jQuery\d+\(\[(.*)\]\)', price).group(1))
            return float(price_json.get('p', 0))
        except Exception as e:
            return 0

    def get_comment(self,url):
        '''商品的评论数'''
        try:
            id = re.match(r'.*?(\d+)\.html', url).group(1)
            comment_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}&callback=jQuery5549764&_={}'.format(id, int(time.time()*1000))
            comment = requests.get(comment_url,headers=self.headers,verify=False).text
            comment_json = json.loads(re.match(r'.*?\[(.*)\]',comment).group(1))
            comment_count = comment_json.get('CommentCount', '')
            good_rate = comment_json.get('GoodRate', '')
            poor_rate = comment_json.get('PoorRate', '')
            return (comment_count,good_rate,poor_rate)
        except Exception as e:
            return ('','','')

    def join_list(self, res):
        '''拼接获取到的列表中的数据并去掉空格'''
        result = '|'.join(res).strip()
        return result
