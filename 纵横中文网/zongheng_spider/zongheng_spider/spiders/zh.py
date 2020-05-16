# -*- coding: utf-8 -*-
import scrapy
import re
import time

from fake_useragent import UserAgent
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from zongheng_spider.items import ZonghengSpiderItem


class ZhSpider(CrawlSpider):
    name = 'zh'
    allowed_domains = ['zongheng.com']
    start_urls = [
        'http://book.zongheng.com/store/c0/c0/b0/u0/p1/v9/s9/t0/u0/i1/ALL.html',
        # 'http://book.zongheng.com/store/c0/c0/b0/u0/p2/v9/s9/t0/u0/i1/ALL.html'
    ]

    # base_url = 'http://book.zongheng.com/store/c0/c0/b0/u0/p{}/v9/s9/t0/u0/i1/ALL.html'

    rules = (
        # Rule(LinkExtractor(allow=r'http://book.zongheng.com/store/c0/c0/b0/u0/p\d+/v9/s9/t0/u0/i1/ALL.html'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'http://book.zongheng.com/book/\d+.html'), callback='detail', follow=True),
    )

    def parse_item(self, response):
        # print('-' * 50)
        # print(response.url)

        # 书的链接
        urls = response.xpath('//div[@class="store_collist"]//div[@class="bookimg"]/a/@href').extract()
        # 书的标题
        titles = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookname"]/a/text()').extract()
        # 作者
        authors = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[1]/text()').extract()
        # 作者主页
        authors_urls = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[1]/@href').extract()
        # 书的分类
        categories = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[2]/text()').extract()
        # 分类的链接
        category_urls = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[2]/@href').extract()
        # 更新状态
        status = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/span[1]/text()').extract()
        # 更新时间
        update_times = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/span[2]/text()').extract()
        # 书的简介
        intros = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookintro"]/text()').extract()
        # 最新章节
        book_updates = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookupdate"]/a/text()').extract()
        # 最新章节url
        update_urls = response.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookupdate"]/a/@href').extract()
        # print(urls, titles, authors_urls, authors, category_urls, categories, status, update_times, intros, book_updates)
        # 将一页中所有的书的信息通过zip对应
        all_contents = zip(urls, titles, authors, authors_urls, categories, category_urls, status, update_times, intros, book_updates, update_urls)
        for url, title, author, author_url, category, category_url, status, update_time, intro, book_update, update_url in all_contents:
            item = dict()
            item['spider_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['url'] = url
            item['title'] = title
            item['author'] = author
            item['author_url'] = author_url
            item['status'] = self.status_strip(status)
            item['update_time'] = self.update_time_re(update_time)
            item['intro'] = intro
            item['category'] = category
            item['category_url'] = category_url
            item['book_update'] = book_update
            item['update_url'] = update_url

            # print(item)
            yield item
            # yield scrapy.Request(item)

    def detail(self, response):
        item = {}
        # item = ZonghengItem()
        # item.update(response.meta['contents'])
        # 字数
        number = response.xpath('//div[@class="book-info"]/div[@class="nums"]/span[1]/i/text()').extract()
        # 总推荐
        all_recommend = response.xpath('//div[@class="book-info"]/div[@class="nums"]/span[2]/i/text()').extract()
        # 总点击
        click_num = response.xpath('//div[@class="book-info"]/div[@class="nums"]/span[3]/i/text()').extract()
        # 周推荐
        week_recommend = response.xpath('//div[@class="book-info"]/div[@class="nums"]/span[4]/i/text()').extract()
        item['spider_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['number'] = self.join_str(number)
        item['all_recommend'] = self.join_str(all_recommend)
        item['click_num'] = self.join_str(click_num)
        item['week_recommend'] = self.join_str(week_recommend)

        print(item)
        yield item

    @staticmethod
    def status_strip(in_content):
        """去掉字符中的空格"""
        return in_content.strip()

    @staticmethod
    def update_time_re(in_content):
        """提取更新时间"""
        de_strip = in_content.strip()
        try:
            # 提取时间
            res = re.findall(r'(\d+\-\d+\s+\d+\:\d+)', de_strip)[0]
        except Exception as e:
            return de_strip
        else:
            return res

    @staticmethod
    def join_str(in_join):
        """提取书籍中详细的字数等，将'万'转化位10000"""
        join_res = ''.join(in_join)
        if join_res:
            try:
                # 匹配字符中是否有万
                num_re = re.findall(r'(.*?)万', join_res)[0]
            except:
                # 没有万则直接转化原数字
                num = eval(join_res)
            else:
                # 有万的话转化位10000
                num = eval(num_re) * 10000
        else:
            num = 0
        return int(num)

