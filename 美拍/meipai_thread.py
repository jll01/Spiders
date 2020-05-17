#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   meipai.py
# @Time    :   2020/5/4 21:35
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import random
import os
import pymysql
import json

from queue import Queue
from js2py_my import js2py_main
from fake_useragent import UserAgent
from threading import Thread, Lock


class MeiPai(object):
    def __init__(self, save_video, save_user, save_comment, save_down):
        self.save_video = save_video
        self.save_user = save_user
        self.save_comment = save_comment
        self.save_down = save_down
        # 获取城市代码
        self.city_url = '''https://www.meipai.com/locations/get_province_city_by_country_id?cid={}'''
        # 获取视频信息
        self.url = '''https://www.meipai.com/home/hot_timeline?page=1&count=12'''
        # 视频评论url
        self.comment_url = '''https://www.meipai.com/medias/comments_timeline?page={}&count=10&id={}'''  # 1204187052
        # 下载视频路径
        self.video_path = r'E:\Study\项目\005爬虫\Spiders\美拍\下载\{}.mp4'
        # 城市code文件路径
        self.code_path = r'E:\Study\项目\005爬虫\Spiders\美拍\city_code.json'
        # 保存视频id
        self.save_video_id = []
        # 保存用户id
        self.save_user_id = []
        # 保存评论id
        self.save_comment_id = []
        # 城市code
        self.city_code = {}
        # 视频queue
        self.video_queue = Queue()
        # 用户queue
        self.user_queue = Queue()
        # 评论queue
        self.comment_queue = Queue()
        # 保存comment url
        self.get_comment_queue = Queue()
        # 下载视频
        self.download_queue = Queue()
        # 保存video信息lock
        self.video_lock = Lock()
        # 保存user信息lock
        self.user_lock = Lock()
        # 保存comment信息lock
        self.comment_lock = Lock()
        # 获取视频页码数
        # self.num = num
        # 获取视频保存路径下所有文件
        self.file_list = os.listdir(r'E:\Study\项目\005爬虫\Spiders\美拍\下载')
        # video连接mysql
        self.video_connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.video_cur = self.video_connect.cursor()
        # user连接mysql
        self.user_connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.user_cur = self.user_connect.cursor()
        # comment连接mysql
        self.comment_connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.comment_cur = self.comment_connect.cursor()
        # 判断put队列是否结束
        self.flag = True

    def get_json_info(self):
        """
        获取视频和用户的json数据
        """
        i = 1
        while True:
            headers = {
                'User-Agent': UserAgent().random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Cookie': "MUSID=7tbos07jmslt847697h7tbsml7; sid=7tbos07jmslt847697h7tbsml7; UM_distinctid=171e49370c4f5-0a8941f624bb11-c373667-144000-171e49370c54cf; MP_WEB_GID=365077837234755; virtual_device_id=f0223988f9b30ab2f30f2d9d81247731; pvid=Ef8Wjj2%2FatZsiVFvt%2FIOVi1bbz2voMqm; CNZZDATA1256786412=910314024-1588676805-%7C1588995742",
                'Host': 'www.meipai.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
            try:
                json_page = requests.get(self.url, headers=headers)
                # 当状态码为200,即请求成功
                if json_page.status_code == 200:
                    # 获取json格式的数据
                    try:
                        all_json = json_page.json()
                        contents = all_json.get('medias')
                        # 保存到视频信息队列
                        self.video_queue.put(contents)
                        # 保存到用户信息队列
                        self.user_queue.put(contents)
                        # 保存到评论信息队列
                        self.comment_queue.put(contents)
                        # 保存到下载视频队列
                        self.download_queue.put(contents)

                        print('第{}页的相关视频信息添加完成！'.format(i))
                        i += 1
                        time.sleep(random.uniform(0.5, 1.2))
                    except Exception as e:
                        print('{}出错{}'.format(json_page, e))
                        time.sleep(random.uniform(3, 6))
                else:
                    self.flag = False
                    break
            except Exception as e:
                print('第{}页的相关视频信息获取失败！'.format(i))

    def get_video_info(self):
        """
        获取视频信息
        """
        while True:
            if not self.video_queue.empty():
                contents = self.video_queue.get()
                for content in contents:
                    try:
                        item = dict()
                        # 视频id
                        item['video_id'] = content.get('id', 'Null')
                        # 当视频id在save_video_id中或者视频已经下载保存到本地时
                        if item['video_id'] in self.save_video_id:
                            print("{}视频信息已在数据库中！".format(item['video_id']))
                        else:
                            # 不在save_video_id中将视频id保存
                            self.save_video_id.append(item['video_id'])

                            # 用户id
                            user = content.get('user', 'Null')
                            if user != 'Null':
                                item['user_id'] = user.get('id', 0)

                            item['client_id'] = content.get('client_id', 'Null')
                            # 说明文字
                            item['caption'] = content.get('caption', 'Null')
                            # 视频链接
                            item['url'] = content.get('url', 'Null')
                            # 种类
                            item['category'] = content.get('category', 'Null')
                            # 视频时长
                            item['time'] = content.get('time', 0)
                            # 是否是长视频
                            item['is_long'] = content.get('is_long', 0)
                            # 分辨率
                            item['pic_size'] = content.get('pic_size', 0)
                            # 发布时间
                            item['created_at'] = content.get('created_at', 'Null')
                            # 评论总数
                            item['comments_count'] = str(content.get('comments_count', 0)).replace('<em class="my-count-em">', '').replace('</em>', '')
                            # 点赞
                            item['likes_count'] = str(content.get('likes_count', 0)).replace('<em class="my-count-em">', '').replace('</em>', '')
                            # 转发
                            item['reposts_count'] = str(content.get('reposts_count', 0)).replace('<em class="my-count-em">', '').replace('</em>', '')
                            # 提取并解析视频下载url
                            video_down = js2py_main(content.get('video', 'Null'))
                            if video_down != 0:
                                item['video_down_url'] = video_down
                            else:
                                item['video_down_url'] = 'Null'
                            # 保存视频信息
                            self.save_video_info(item)
                    except Exception as e:
                        print('一条视频信息出错{}'.format(e))

                time.sleep(random.uniform(0.5, 1.5))

            elif self.flag:
                time.sleep(random.uniform(5, 10))
            else:
                break

    def get_user_info(self):
        """
        用户信息
        """
        while self.flag:
            if not self.user_queue.empty():
                contents = self.user_queue.get()
                for content in contents:
                    user = content.get('user', 'Null')
                    if user != 'Null':
                        try:
                            item_user = dict()
                            # 用户id
                            item_user['user_id'] = user.get('id', 0)
                            # 如果用户id不在self.save_user_id中将其添加到self.save_user_id
                            if item_user['user_id'] not in self.save_user_id:
                                self.save_user_id.append(item_user['user_id'])
                                # 昵称
                                item_user['screen_name'] = user.get('screen_name', 'Null')
                                # 用户所在国家
                                country = user.get('country', 0)
                                # 用户所在省份
                                province = user.get('province', 0)
                                # 用户所在城市
                                city = user.get('city', 0)
                                # 编码转换为名称
                                item_user['country'], item_user['province'], item_user['city'] = self.city_code2city(country, province, city)
                                # 性别
                                item_user['gender'] = self.change_gender(user.get('gender', 'Null'))

                                item_user['birthday'] = user.get('birthday', 'Null')
                                item_user['age'] = user.get('age', 0)
                                # 星座
                                item_user['constellation'] = user.get('constellation', 'Null')
                                # 认证
                                item_user['verified'] = user.get('verified', False)
                                # 粉丝
                                item_user['followers_count'] = user.get('followers_count', 0)
                                # 关注
                                item_user['friends_count'] = user.get('friends_count', 0)
                                # 转发
                                item_user['user_reposts_count'] = user.get('reposts_count', 0)
                                # 视频数量
                                item_user['videos_count'] = user.get('videos_count', 0)
                                # 用户主页
                                item_user['user_url'] = user.get('url', 'Null')
                                # 用户创建时间
                                item_user['user_created_at'] = user.get('created_at', 'Null')
                                # 总点赞数
                                item_user['be_liked_count'] = user.get('be_liked_count', 0)

                                self.save_user_info(item_user)
                            else:
                                print('{}用户已在数据库中！'.format(item_user['user_id']))
                        except Exception as e:
                            print('一条用户信息出错{}'.format(e))

                time.sleep(random.uniform(0.5, 1.2))
            elif self.flag:
                time.sleep(random.uniform(5, 10))
            else:
                break

    def put_comment_info(self):
        """
        将每个视频的评论信息添加到队列中
        """
        while True:
            if not self.comment_queue.empty():
                contents = self.comment_queue.get()
                comment_l = []
                for content in contents:
                    video_id = content.get('id', 'Null')
                    if video_id != 'Null':
                        comment_thread = Thread(target=self.get_comment_info, args=(video_id,))
                        comment_thread.start()
                        comment_l.append(comment_thread)

                for i in comment_l:
                    i.join()
            elif self.flag:
                time.sleep(random.uniform(5, 10))
            else:
                break

    def get_comment_info(self, video_id):
        """
        获取每个视频的评论
        :param video_id: 视频id
        :return:
        """
        com_num = 1
        while True:
            video_com = requests.get(self.comment_url.format(com_num, video_id), headers={'User-Agent': UserAgent().random})
            content = video_com.json()
            if content:
                for i in range(len(content)):
                    item = dict()
                    # 评论id
                    item['comment_id'] = content[i].get('id', 0)
                    if item['comment_id'] not in self.save_comment_id:
                        self.save_comment_id.append(item['comment_id'])
                        # 视频id
                        item['video_id'] = content[i].get('media_id', 0)
                        # 评论用户id
                        item['user_id'] = content[i].get('uid', 0)
                        # 评论内容
                        item['content'] = content[i].get('content_origin', 'Null')
                        # 评论时间
                        item['comment_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(content[i].get('created_at_origin', time.time())))

                        # 保存到数据库
                        self.save_comment_info(item, com_num, i+1)

                time.sleep(random.uniform(0.5, 2))
                com_num += 1
            else:
                break

        print('{}.mp4的评论获取完成！'.format(video_id))

    def put_download_info(self):
        while True:
            if not self.download_queue.empty():
                contents = self.download_queue.get()
                download_l = []

                for content in contents:
                    video_id = content.get('id', 'Null')
                    # 提取并解析视频下载url
                    video_down = js2py_main(content.get('video', 'Null'))
                    if video_down != 0:
                        video_down_url = video_down
                    else:
                        video_down_url = 'Null'
                    if video_id != 'Null' and video_down_url != 'Null' and '{}.mp4'.format(video_id) not in self.file_list:
                        download_thread = Thread(target=self.download_video, args=(video_down_url, video_id))
                        download_thread.start()
                        download_l.append(download_thread)
                    else:
                        print('{}下载失败！'.format(url))

                for i in download_l:
                    i.join()

                time.sleep(random.uniform(0.5, 1))
            elif self.flag:
                time.sleep(random.uniform(5, 10))
            else:
                break

    def download_video(self, url, video_id):
        """
        下载视频到本地
        :param url: 视频现在的链接
        :param video_id: 视频的id
        """
        print('{}.mp4开始下载！请稍后！'.format(video_id))
        # 视频下载url请求
        res = requests.get(url, headers={'User-Agent': UserAgent().random}, stream=True)
        temp_size = 0
        if res.status_code == 200:
            with open(self.video_path.format(video_id), 'wb') as file:
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        temp_size += len(chunk)
                        file.write(chunk)
                        file.flush()  # 刷新缓存
                print("{}.mp4下载完成！".format(video_id))
        else:
            print('{}.mp4下载失败！'.format(url))

    def from_sql_get_id(self):
        """
        从数据库中查询已经保存了的user_id,video_id,comment_id进行判断后避免重复保存用户信息
        """
        # 获取保存到数据库中的用户id
        sql_user = "select user_id from mp_user"
        self.video_cur.execute(sql_user)
        for i in self.video_cur.fetchall():
            self.save_user_id.append(i[0])

        # 获取保存到数据库中的视频id
        sql_video = "select video_id from mp_video"
        self.video_cur.execute(sql_video)
        for i in self.video_cur.fetchall():
            self.save_video_id.append(i[0])

        # 获取保存到数据库中的评论id
        sql_comment = "select comment_id from mp_comment"
        self.video_cur.execute(sql_comment)
        for i in self.video_cur.fetchall():
            self.save_comment_id.append(i[0])

    def get_city_code(self):
        """
        获取用户所在的地区并保存到本地json文件中
        """
        city_code_json = {}
        # 初始id
        code_num = 1000000
        while True:
            code_json = requests.get(self.city_url.format(code_num)).json()
            if code_json:
                city_code_json[code_num] = code_json
                code_num += 10000
                time.sleep(random.uniform(0.5, 1))
            else:
                break

        with open(self.code_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(city_code_json, ensure_ascii=False))
        print(r'城市与code转换文件已保存到{}中!'.format(self.code_path))

    def city_code2city(self, country, province, city):
        """
        将该用户的地区code转换成名称
        :param country: 国家
        :param province: 省份
        :param city: 城市
        :return: 转换后的名称
        """
        try:
            # 当国家的code为0的时候国家、省、市为未知
            if country != 0:
                code2country = self.city_code[str(country)]["country"]
                if province != 0:
                    code2province = self.city_code[str(country)]["provinces"][str(province)]["province"]
                    if city != 0:
                        code2city = self.city_code[str(country)]["provinces"][str(province)]["citys"][str(city)]
                    else:
                        code2city = code2province
                else:
                    # 当省为0，省市和国家名一样
                    code2province, code2city = code2country, code2country
            else:
                code2country, code2province, code2city = '未知', '未知', '未知'
        except Exception as e:
            code2country, code2province, code2city = '未知', '未知', '未知'
        return code2country, code2province, code2city

    @staticmethod
    def change_gender(gender):
        """
        将性别f和m转换成男女
        :param gender: 性别m和f
        :return: 男或女
        """
        ch_gen = '未知'
        if gender == 'f':
            ch_gen = '女'
        elif gender == 'm':
            ch_gen = '男'

        return ch_gen

    def save_video_info(self, item):
        """
        保存视频信息到mysql数据库
        """
        self.video_lock.acquire()
        try:
            self.video_cur.execute(
                '''insert into mp_video (video_id,user_id,client_id,caption,url,category,time,is_long,pic_size,created_at,comments_count,likes_count,reposts_count,video_down_url) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['video_id'],
                    item['user_id'],
                    item['client_id'],
                    item['caption'],
                    item['url'],
                    item['category'],
                    item['time'],
                    item['is_long'],
                    item['pic_size'],
                    item['created_at'],
                    item['comments_count'],
                    item['likes_count'],
                    item['reposts_count'],
                    item['video_down_url'],
                )
            )
            self.video_connect.commit()
            print('{}视频信息已经保存到数据库！'.format(item['video_id']))
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))
        self.video_lock.release()

    def save_user_info(self, item):
        """
        保存用户信息到mysql数据库
        """
        self.user_lock.acquire()
        try:
            self.user_cur.execute(
                '''insert into mp_user (user_id,screen_name,country,province,city,gender,birthday,age,constellation,verified,followers_count,friends_count,user_reposts_count,videos_count,user_url,user_created_at,be_liked_count) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['user_id'],
                    item['screen_name'],
                    item['country'],
                    item['province'],
                    item['city'],
                    item['gender'],
                    item['birthday'] ,
                    item['age'],
                    item['constellation'],
                    item['verified'],
                    item['followers_count'],
                    item['friends_count'],
                    item['user_reposts_count'],
                    item['videos_count'],
                    item['user_url'],
                    item['user_created_at'],
                    item['be_liked_count'],
                )
            )
            self.user_connect.commit()
            print('{}用户信息已经保存到数据库！'.format(item['user_id']))
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))
        self.user_lock.release()

    def save_comment_info(self, item, page_num, save_num):
        """
        保存用户评论信息到mysql数据库
        """
        self.comment_lock.acquire()
        try:
            self.comment_cur.execute(
                '''insert into mp_comment (comment_id,video_id,user_id,content,comment_date) values (%s,%s,%s,%s,%s)''',
                (
                    item['comment_id'],
                    item['video_id'],
                    item['user_id'],
                    item['content'],
                    item['comment_date'],
                )
            )
            self.comment_connect.commit()
            print('{}.mp4第{}页第{}条评论已保存到数据库!'.format(item['video_id'], page_num, save_num))
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))

        self.comment_lock.release()

    def main(self):
        """
        调用接口
        """
        if not os.path.exists(self.code_path):
            self.get_city_code()
        else:
            with open(self.code_path, 'r', encoding='utf-8') as f:
                self.city_code.update(json.loads(f.read()))
        self.from_sql_get_id()

        json_thread = Thread(target=self.get_json_info)
        json_thread.start()
        time.sleep(2)

        if self.save_video == 'y':
            video_thread = Thread(target=self.get_video_info)
            video_thread.start()

        if self.save_user == 'y':
            user_thread = Thread(target=self.get_user_info)
            user_thread.start()

        if self.save_comment == 'y':
            comment_thread = Thread(target=self.put_comment_info)
            comment_thread.start()

        if self.save_down == 'y':
            download_thread = Thread(target=self.put_download_info)
            download_thread.start()

        json_thread.join()
        if self.save_video == 'y':
            video_thread.join()
        if self.save_user == 'y':
            user_thread.join()

        if self.save_comment == 'y':
            comment_thread.join()

        if self.save_down == 'y':
            download_thread.join()


if __name__ == '__main__':
    if_video = input('请输入是否获取视频信息(y/n)：').strip().lower()
    if_user = input('请输入是否获取用户信息(y/n)：').strip().lower()
    if_comment = input('请输入是否获取视频评论信息(y/n)：').strip().lower()
    if_down = input('请输入是否下载视频(y/n)：').strip().lower()
    mp = MeiPai(if_video, if_user, if_comment, if_down)
    mp.main()
