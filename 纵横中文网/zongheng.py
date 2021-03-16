import requests
import time
import random
import re
import json
import pymysql

from lxml import etree
from fake_useragent import UserAgent


class ZongHeng(object):
    def __init__(self, page):
        self.url = 'http://book.zongheng.com/store/c0/c0/b0/u0/p{}/v9/s9/t0/u0/i1/ALL.html'
        # 页码变化
        self.num = 1
        self.page = page
        self.useragent = UserAgent()
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', password='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def geturl(self):
        """获取页面中所有书的链接、标题等信息"""
        while self.num <= self.page:
            header = {
                'User-Agent': self.useragent.random
            }
            req = requests.get(self.url.format(self.num), headers=header).text
            html = etree.HTML(req)
            # 书的链接
            urls = html.xpath('//div[@class="store_collist"]//div[@class="bookimg"]/a/@href')
            # 书的标题
            titles = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookname"]/a/text()')
            # 作者
            authors = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[1]/text()')
            # 作者主页
            authors_urls = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[1]/@href')
            # 书的分类
            categories = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[2]/text()')
            # 分类的链接
            category_urls = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/a[2]/@href')
            # 更新状态
            status = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/span[1]/text()')
            # 更新时间
            update_times = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookilnk"]/span[2]/text()')
            # 书的简介
            intros = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookintro"]/text()')
            # 最新章节
            book_updates = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookupdate"]/a/text()')
            # 最新章节url
            update_urls = html.xpath('//div[@class="store_collist"]//div[@class="bookinfo"]/div[@class="bookupdate"]/a/@href')
            # print(urls, titles, authors_urls, authors, category_urls, categories, status, update_times, intros, book_updates)
            # 将一页中所有的书的信息通过zip对应
            all_contents = zip(urls, titles, authors, authors_urls, categories, category_urls, status, update_times, intros, book_updates, update_urls)
            for url, title, author, author_url, category, category_url, status, update_time, intro, book_update, update_url in all_contents:
                item = dict()
                item['url'] = url
                item['title'] = title
                item['author'] = author
                item['author_url'] = author_url
                item['category'] = category
                item['category_url'] = category_url
                item['status'] = self.status_strip(status)
                item['update_time'] = self.update_time_re(update_time)
                item['intro'] = intro
                item['book_update'] = book_update
                item['update_url'] = update_url

                self.getdetail(item)
                time.sleep(random.uniform(1, 3))

            self.num += 1
            time.sleep(random.uniform(2, 5))

    def getdetail(self, contents):
        """获取每本书的详细信息"""
        detail_con = requests.get(contents['url'], headers={'User-Agent': self.useragent.random}).text
        html_con = etree.HTML(detail_con)
        # 字数
        number = html_con.xpath('//div[@class="book-info"]/div[@class="nums"]/span[1]/i/text()')
        # 总推荐
        all_recommend = html_con.xpath('//div[@class="book-info"]/div[@class="nums"]/span[2]/i/text()')
        # 总点击
        click_num = html_con.xpath('//div[@class="book-info"]/div[@class="nums"]/span[3]/i/text()')
        # 周推荐
        week_recommend = html_con.xpath('//div[@class="book-info"]/div[@class="nums"]/span[4]/i/text()')
        contents['number'] = self.join_str(number)
        contents['all_recommend'] = self.join_str(all_recommend)
        contents['click_num'] = self.join_str(click_num)
        contents['week_recommend'] = self.join_str(week_recommend)
        contents['spider_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print(contents)
        self.save_json(contents)
        self.save_mysql(contents)

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

    @staticmethod
    def save_json(item):
        """保存每本书的信息道json文件中"""
        with open('纵横中文.json', 'a', encoding='utf-8') as file:
            file.write(json.dumps(item, ensure_ascii=False) + '\n')

    def save_mysql(self, item):
        self.cur.execute(
            """insert into zongheng (spider_time, url, title, author, author_url, category, category_url, status, update_time, intro, book_update, update_url, 
            number, all_recommend, click_num, week_recommend) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                item['spider_time'],
                item['url'],
                item['title'],
                item['author'],
                item['author_url'],
                item['category'],
                item['category_url'],
                item['status'],
                item['update_time'],
                item['intro'],
                item['book_update'],
                item['update_url'],
                item['number'],
                item['all_recommend'],
                item['click_num'],
                item['week_recommend']
            )
        )
        self.connect.commit()

    def main(self):
        self.geturl()


if __name__ == '__main__':
    zh = ZongHeng(2)
    zh.main()
