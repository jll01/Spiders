import requests
import json
import time
import random
import urllib3
import re
import pymysql

from lxml import etree


class DoubanMovie(object):
    def __init__(self):
        self.geturl = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=&start={}'
        self.geturl_start = 0

        self.reviewsurl = '{}reviews?start=0'
        # self.reviewsstart = 0

        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            # 'Host': 'movie.douban.com'
        }
        self.connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cur = self.connect.cursor()

    def get_subject_url(self):
        while True:
            req = requests.get(self.geturl.format(self.geturl_start),headers=self.headers, verify=False).text
            datas = json.loads(req)
            urls = datas.get('data')
            if len(urls) != 0:
                for url in urls:
                    self.subject(url.get('url'),url.get('id'))
                self.geturl_start += 20
                time.sleep(random.uniform(2,4))
            else:
                break

    def subject(self,url,movieid):
        req = requests.get(url,headers=self.headers,verify=False).text
        html = etree.HTML(req)
        dict_data = html.xpath('//script[@type="application/ld+json"]/text()')
        try:
            json_data = json.loads(dict_data[0].replace('\n', ''))
            item = {}
            item['movieid'] = movieid
            item['name'] = json_data.get('name','')
            item['rename'] = ''.join(re.findall(r'<span class="pl">又名:</span>(.*?)<br/>',req)).replace(' ','')

            item['country'] = ''.join(re.findall(r'<span class="pl">制片国家/地区:</span>(.*?)<br/>',req)).replace(' ','')
            item['movielanguage'] = ''.join(re.findall(r'<span class="pl">语言:</span>(.*?)<br/>',req)).replace(' ','')

            item['url'] = url
            item['image'] = json_data.get('image','')

            item['directors'] = self.join_person(json_data.get('director'))
            item['author'] = self.join_person(json_data.get('author'))
            item['actor'] = self.join_person(json_data.get('actor'))

            item['publish'] = json_data.get('datePublished','')
            item['genres'] = '|'.join(json_data.get('genre',''))

            item['duration'] = ''.join(re.findall(r'<span class="pl">片长:</span> <span property="v:runtime" content="\d+">(.*?)</span><br/>',req)).replace(' ','')
            item['description'] = json_data.get('description','')
            item['type'] = json_data.get('@type','')

            aggregateRating = json_data.get('aggregateRating','')
            item['ratingCount'] = eval(aggregateRating.get('ratingCount','0'))
            item['ratingValue'] = eval(aggregateRating.get('ratingValue','0'))

            print(item)
            self.get_reviews(url,item['movieid'])
            self.save_subject(item)

        except Exception as e:
            print(e)
        finally:
            time.sleep(random.uniform(1,2))

    def get_reviews(self,url,movieid):
        print('----------{}的影评----------'.format(movieid))
        req = requests.get(self.reviewsurl.format(url), headers=self.headers, verify=False).text
        html = etree.HTML(req)

        image = html.xpath('//div[@class="review-list  "]/div/div/header[@class="main-hd"]/a/img/@src')
        name = html.xpath('//div[@class="review-list  "]/div/div/header[@class="main-hd"]/a[@class="name"]/text()')
        appraise = html.xpath('//div[@class="review-list  "]/div/div/header[@class="main-hd"]/span/@title')
        time = html.xpath('//div[@class="review-list  "]/div/div/header[@class="main-hd"]/span[@class="main-meta"]/text()')
        title = html.xpath('//div[@class="review-list  "]/div/div/div[@class="main-bd"]/h2/a/text()')
        contents = html.xpath('//div[@class="review-list  "]/div/div/div[@class="main-bd"]/div[@class="review-short"]/div[@class="short-content"]/text()')
        content = ''.join(contents).replace('\n','').replace(' ','').split('\xa0()')
        useful = html.xpath('//div[@class="review-list  "]/div/div/div[@class="main-bd"]/div[@class="action"]/a[@title="有用"]/span/text()')
        useless = html.xpath('//div[@class="review-list  "]/div/div/div[@class="main-bd"]/div[@class="action"]/a[@title="没用"]/span/text()')
        reply = html.xpath('//div[@class="review-list  "]/div/div/div[@class="main-bd"]/div[@class="action"]/a[@class="reply "]/text()')

        for image,name,appraise,time,title,content,useful,useless,reply in zip(image,name,appraise,time,title,content,useful,useless,reply):
            item = {}
            item['movieid'] = movieid
            item['image'] = image
            item['name'] = name
            item['appraise'] = appraise
            item['time'] = time
            item['title'] = title
            item['content'] = content
            item['useful'] = useful.replace('\n','').replace(' ','')
            item['useless'] = useless.replace('\n','').replace(' ','')
            item['reply'] = reply.replace('\n','').replace(' ','').replace('回应','')

            print(item)
            self.save_reviews(item)

    def join_person(self,persons):
        person_list = []
        for person in persons:
            person_list.append(person.get('name', ''))

        return '|'.join(person_list)

    def save_subject(self,item):
        try:
            self.cur.execute(
                '''insert into douban_subject (movieid,name,re_name,country,movielanguage,url,image,directors,author,actor,publish,genres,duration,description,type,ratingCount,ratingValue) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['movieid'],
                    item['name'],
                    item['rename'],
                    item['country'],
                    item['movielanguage'],
                    item['url'],
                    item['image'],
                    item['directors'],
                    item['author'],
                    item['actor'],
                    item['publish'],
                    item['genres'],
                    item['duration'],
                    item['description'],
                    item['type'],
                    item['ratingCount'],
                    item['ratingValue'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print(e)

    def save_reviews(self,item):
        try:
            self.cur.execute(
                '''insert into douban_reviews (movieid,image,name,appraise,time,title,content,useful,useless,reply) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['movieid'],
                    item['image'],
                    item['name'],
                    item['appraise'],
                    item['time'],
                    item['title'],
                    item['content'],
                    item['useful'],
                    item['useless'],
                    item['reply'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print(e)

    def main(self):
        self.get_subject_url()


if __name__ == '__main__':
    urllib3.disable_warnings()

    douban = DoubanMovie()
    douban.main()
