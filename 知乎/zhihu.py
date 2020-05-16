#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   009zhihu.py
# @Time    :   2019/7/6 18:37
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import urllib3
import json
import datetime
import pymysql

from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ZhiHu(object):
    def __init__(self,username,passwd,url,pagenum):

        # 用户名
        self.username = username
        # 密码
        self.passwd = passwd
        # 登陆url
        self.login_url = url
        # 首页url
        self.data_url = 'https://www.zhihu.com/'
        # IP代理
        ip = [
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
            'http': random.choice(ip),
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
        }
        self.session = requests.session()
        # 获取数据时拼接url所需参数
        self.page = 2
        self.after_id = 5
        # 提取数据的页码数量
        self.pagenum = pagenum
        # 问题总数
        self.count = 0
        # 提取错误的总数
        self.error_count = 0
        # 数据库
        self.connect = pymysql.connect(host='localhost',port=3306,user='root',passwd='0000',db='scrapytest')
        self.cur = self.connect.cursor()

    def login(self):
        '''selenium模拟登陆'''
        chrome_options = Options()
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_drive = r'D:\soft\Chrome\chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=chrome_drive, options=chrome_options)

        self.driver.get(self.login_url)
        time.sleep(5)
        self.driver.find_element_by_xpath('//div[@class="SignFlowHomepage"]//div[@class="SignContainer-inner"]//div[@class="SignFlow-tabs"]/div[2]').click()
        time.sleep(2)
        self.driver.find_element_by_xpath('//main[@class="App-main"]//div[@class="SignContainer-inner"]//div[@class="SignFlow-account"]//input').send_keys(self.username)
        time.sleep(1)
        self.driver.find_element_by_xpath('//main[@class="App-main"]//div[@class="SignContainer-inner"]//div[@class="SignFlow-password"]//input').send_keys(self.passwd)
        time.sleep(10)
        self.driver.find_element_by_xpath('//main[@class="App-main"]//div[@class="SignContainer-inner"]//button[@type="submit"]').click()
        time.sleep(3)

    def get_cookie(self):
        '''获取selenium登陆时的cookie'''
        cookies = self.driver.get_cookies()
        save_cookie = {}
        for i in cookies:
            save_cookie[i['name']] = i['value']
            requests.utils.add_dict_to_cookiejar(self.session.cookies,{i['name']: i['value']})

        with open('cookie.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(save_cookie))

    def change_time(self,res):
        '''时间转换'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(res))

    def utc2local(self,utc_dtm):
        '''UTC 时间转本地时间（ +8:00 ）'''
        local_tm = datetime.datetime.fromtimestamp(0)
        utc_tm = datetime.datetime.utcfromtimestamp(0)
        ls = datetime.datetime.strptime(utc_dtm, '%Y-%m-%dT%H:%M:%S.000Z')
        offset = local_tm - utc_tm
        return str(ls + offset)

    def join_null(self,res):
        '''拼接列表'''
        return ''.join(res)

    def str2num(self,res):
        '''字符串转换数字'''
        try:
            return int(res)
        except Exception as e:
            return 0

    def save_data(self,item):
        '''保存数据'''
        self.cur.execute(
            """insert into zhihu (question_id,title,question_url,tags,answerCount,commentCount,dateCreated,dateModified,followerCount,readCount,name,author_url,author_image,answer_id,answer_url,answer_content,answer_image,answer_publishtime,answer_edittime,answer_commentcount,answer_agreecount) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['question_id'],
                item['title'],
                item['question_url'],
                item['tags'],
                item['answerCount'],
                item['commentCount'],
                item['dateCreated'],
                item['dateModified'],
                item['followerCount'],
                item['readCount'],
                item['name'],
                item['author_url'],
                item['author_image'],
                item['answer_id'],
                item['answer_url'],
                item['answer_content'],
                item['answer_image'],
                item['answer_publishtime'],
                item['answer_edittime'],
                item['answer_commentcount'],
                item['answer_agreecount'],
            ))
        self.connect.commit()

    def about_question(self,question_id,answer_id):
        '''提取详情页面'''
        question_url = 'https://www.zhihu.com/question/{}/answer/{}'.format(question_id,answer_id)
        response = self.session.get(question_url, headers=self.headers,verify=False).text
        html = etree.HTML(response)
        item = {}
        # 问题id
        item['question_id'] = question_id
        questions = html.xpath('//main[@class="App-main"]/div[@class="QuestionPage"]')
        for question in questions:
            # 问题标题
            item['title'] = self.join_null(question.xpath('./meta[@itemprop="name"]/@content'))
            # 问题url
            item['question_url'] = self.join_null(question.xpath('./meta[@itemprop="url"]/@content'))
            # 问题标签
            item['tags'] = self.join_null(question.xpath('./meta[@itemprop="keywords"]/@content'))
            # 答案总数
            item['answerCount'] = self.str2num(self.join_null(question.xpath('./meta[@itemprop="answerCount"]/@content')))
            # 问题评论总数
            item['commentCount'] = self.str2num(self.join_null(question.xpath('./meta[@itemprop="commentCount"]/@content')))
            # 问题发布时间
            item['dateCreated'] = self.utc2local(self.join_null(question.xpath('./meta[@itemprop="dateCreated"]/@content')))
            # 问题修改时间
            item['dateModified'] = self.utc2local(self.join_null(question.xpath('./meta[@itemprop="dateModified"]/@content')))
            # 关注者人数
            item['followerCount'] = self.str2num(self.join_null(question.xpath('./meta[@itemprop="zhihu:followerCount"]/@content')))
        # 问题被浏览人数
        item['readCount'] = self.str2num(self.join_null(html.xpath('//div[@class="NumberBoard-item"]/div[@class="NumberBoard-itemInner"]/strong[@class="NumberBoard-itemValue"]/@title')))
        # 作者
        authors = html.xpath('//div[@class="QuestionAnswer-content"]//div[@class="ContentItem-meta"]/div[@itemprop="author"]')
        for author in authors:
            # 昵称
            item['name'] = self.join_null(author.xpath('./meta[@itemprop="name"]/@content'))
            # 作者主页
            item['author_url'] = self.join_null(author.xpath('./meta[@itemprop="url"]/@content'))
            # 作者头像
            item['author_image'] = self.join_null(author.xpath('./meta[@itemprop="image"]/@content'))

        # 答案id
        item['answer_id'] = answer_id
        # 答案url
        item['answer_url'] = question_url

        answers = html.xpath('//div[@class="ListShortcut"]//div[@class="QuestionAnswer-content"]//div[@class="RichContent RichContent--unescapable"]')
        for answer in answers:
            # 答案内容
            item['answer_content'] = self.join_null(answer.xpath('.//span/p/text()'))
            # 答案内容图片
            item['answer_image'] = '|'.join(answer.xpath('.//span/figure[@data-size="normal"]/img/@data-default-watermark-src'))
            # 答案发布时间
            item['answer_publishtime'] = self.join_null(answer.xpath('.//div[@class="ContentItem-time"]//span/@data-tooltip'))[4:]
            # 答案修改时间
            item['answer_edittime'] = self.join_null(answer.xpath('.//div[@class="ContentItem-time"]//span/text()'))[4:]
            # 答案评论数量
            item['answer_commentcount'] = self.str2num(self.join_null(answer.xpath('./div[contains(@class,"ContentItem-actions")]/button[1]/text()')).split(' ',)[0])
        # 答案赞同人数
        item['answer_agreecount'] = self.str2num(self.join_null(html.xpath('//div[@class="ListShortcut"]//div[@class="QuestionAnswer-content"]//div[@class="ContentItem-meta"]/div[@class="AnswerItem-extraInfo"]//button/text()')).split(' ')[0].replace(',', ''))

        print(item)
        self.save_data(item)

    def get_id(self):
        '''获取问题和答案的id'''
        while self.page <= self.pagenum+1:
            url = 'https://www.zhihu.com/api/v3/feed/topstory/recommend?session_token=e15109f3d56be2153dce6b4fbea91b42&desktop=true&page_number={}&limit=6&action=down&after_id={}'.format(self.page, self.after_id)
            response = self.session.get(url, headers=self.headers, verify=False).text
            data_json = json.loads(response)
            try:
                contents = data_json['data']
            except Exception as e:
                print('获取data的时候出错了！{}'.format(e))
            else:
                for content in contents:
                    self.count += 1
                    try:
                        target = content['target']
                        question = target.get('question')
                        # 答案id
                        answer_id = target.get('id')
                        # 问题id
                        question_id = question.get('id')
                        self.about_question(question_id,answer_id)
                    except Exception as e:
                        print('提取id的时候出错！{}'.format(e))
                        self.error_count += 1
                    time.sleep(random.randint(2,3))
            finally:
                print('第{}页下载完成！共提取{}页{}条问题，{}条提取错误'.format(self.page-1,self.page-1,self.count,self.error_count))
                self.page += 1
                self.after_id += 6
                time.sleep(random.randint(3,5))

    def main(self):
        while True:
            with open('cookie.json', 'r') as f:
                cookie = f.read()
            if len(cookie) != 0:
                for key,value in json.loads(cookie).items():
                    requests.utils.add_dict_to_cookiejar(self.session.cookies, {key: value})
                response = self.session.get(self.data_url, headers=self.headers, verify=False)
                with open('test.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                if response.status_code == 200:
                    print('登陆成功！')
                    self.get_id()
                    break
                else:
                    print('登陆失败！')
                    self.login()
                    self.get_cookie()
            else:
                print('登陆失败！')
                self.login()
                self.get_cookie()


if __name__ == '__main__':
    urllib3.disable_warnings()

    username = 18866478984
    password = 'qwertyuiop0123456'
    login_url = 'https://www.zhihu.com/signin'

    pagenum = int(input('请输入要获取的页码数量：'))

    zh = ZhiHu(username,password,login_url,pagenum)
    zh.main()
