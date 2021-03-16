import requests
import time
import random
import os
import pymysql
import json

from js2py_my import js2py_main
from fake_useragent import UserAgent


class MeiPai(object):
    """
    美拍视频下载、视频其他信息和用户信息保存
    """
    def __init__(self, num):
        # 获取城市代码
        self.city_url = '''https://www.meipai.com/locations/get_province_city_by_country_id?cid={}'''
        # 获取视频信息
        self.url = '''https://www.meipai.com/home/hot_timeline?page=1&count=12'''
        # 视频评论url
        self.comment_url = '''https://www.meipai.com/medias/comments_timeline?page={}&count=10&id={}'''  # 1204187052
        # 下载视频路径
        self.video_path = r'****{}.mp4'
        # 保存视频id
        self.save_video_id = []
        # 保存用户id
        self.save_user_id = []
        # 保存评论id
        self.save_comment_id = []
        # 城市code
        self.city_code = {}
        # 获取视频页码数
        self.num = num
        # 连接mysql
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def get_info(self):
        """
        获取视频和用户的json数据
        """
        # 获取视频保存路径下所有文件
        file_list = os.listdir(r'****')

        for i in range(self.num):
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
            json_page = requests.get(self.url, headers=headers)
            # 当状态码为200,即请求成功
            if json_page.status_code == 200:
                # 获取json格式的数据
                all_json = json_page.json()
                contents = all_json.get('medias')
                for content in contents:
                    item = dict()
                    # 视频id
                    item['video_id'] = content.get('id', 'Null')
                    # 当视频id在self.save_video_id中或者视频已经下载保存到本地时
                    if item['video_id'] in self.save_video_id or '{}.mp4'.format(item['video_id']) in file_list:
                        print("{}.mp4已存在！".format(item['video_id']))
                    else:
                        # 不在self.save_video_id中将视频id保存
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
                        # 发布时间
                        item['created_at'] = content.get('created_at', 'Null')
                        # 评论总数
                        item['comments_count'] = content.get('comments_count', 0)
                        # 点赞
                        item['likes_count'] = str(content.get('likes_count', 0)).replace('<em class="my-count-em">', '').replace('</em>', '')
                        # 转发
                        item['reposts_count'] = content.get('reposts_count', 0)
                        # 提取并解析视频下载url
                        video_down = js2py_main(content.get('video', 'Null'))

                        print('{}视频信息获取完成！'.format(item['video_id']))
                        # 获取用户信息
                        self.get_user(user)

                        if video_down != 0:
                            print('{}视频下载url解析完成！'.format(item['video_id']))
                            item['video_down_url'] = video_down
                        else:
                            item['video_down_url'] = 'Null'

                        print('{}视频信息开始保存到数据库！'.format(item['video_id']))
                        self.save_video_info(item)
                        print('{}视频信息已经保存到数据库！'.format(item['video_id']))
                        # 获取该视频的评论
                        print('{}.mp4开始获取评论！'.format(item['video_id']))
                        self.get_comment_content(item['video_id'])
                        # 下载视频
                        self.download_video(item['video_down_url'], item['video_id'])
                    # 每个视频信息输出之间有一行空格
                    print()

            time.sleep(random.uniform(0.5, 2))

    def get_user(self, user):
        """
        用户信息
        :param user: 用户的json数据
        """
        if user != 'Null':
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

                print('{}用户信息获取完成！'.format(item_user['user_id']))

                print('{}用户信息开始保存到数据库！'.format(item_user['user_id']))
                self.save_user_info(item_user)
                print('{}用户信息已经保存到数据库！'.format(item_user['user_id']))

            else:
                print('{}用户已在数据库中！'.format(item_user['user_id']))

    def get_comment_content(self, video_id):
        """
        获取每个视频的评论信息
        :param video_id: 视频的id
        """
        com_num = 1
        while True:
            video_com = requests.get(self.comment_url.format(com_num, video_id))
            video_json = video_com.json()
            if video_json:
                for content in video_json:
                    item = dict()
                    # 评论id
                    item['comment_id'] = content.get('id', 0)
                    if item['comment_id'] not in self.save_comment_id:
                        self.save_comment_id.append(item['comment_id'])
                        # 视频id
                        item['video_id'] = content.get('media_id', 0)
                        # 评论用户id
                        item['user_id'] = content.get('uid', 0)
                        # 评论内容
                        item['content'] = content.get('content_origin', 'Null')
                        # 评论时间
                        item['comment_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(content.get('created_at_origin', time.time())))

                        # 保存到数据库
                        self.save_comment_info(item)
                print('{}.mp4评论第{}页获取完成！'.format(video_id, com_num))
                time.sleep(random.uniform(0.5, 2))
                com_num += 1
            else:
                break

        print('{}.mp4的评论获取完成！'.format(video_id))

    def download_video(self, url, video_id):
        """
        下载视频到本地
        :param url: 视频现在的链接
        :param video_id: 视频的id
        """
        if url != 'Null':
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
                print('{}下载失败！'.format(url))
        else:
            print('{}下载失败！'.format(url))

    def save_video_info(self, item):
        """
        保存视频信息到mysql数据库
        """
        try:
            self.cur.execute(
                '''insert into mp_video (video_id,user_id,client_id,caption,url,category,time,is_long,created_at,comments_count,likes_count,reposts_count,video_down_url) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (
                    item['video_id'],
                    item['user_id'],
                    item['client_id'],
                    item['caption'],
                    item['url'],
                    item['category'],
                    item['time'],
                    item['is_long'],
                    item['created_at'],
                    item['comments_count'],
                    item['likes_count'],
                    item['reposts_count'],
                    item['video_down_url'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))

    def save_user_info(self, item):
        """
        保存用户信息到mysql数据库
        """
        try:
            self.cur.execute(
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
            self.connect.commit()
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))

    def save_comment_info(self, item):
        """
        保存用户评论信息到mysql数据库
        """
        try:
            self.cur.execute(
                '''insert into mp_comment (comment_id,video_id,user_id,content,comment_date) values (%s,%s,%s,%s,%s)''',
                (
                    item['comment_id'],
                    item['video_id'],
                    item['user_id'],
                    item['content'],
                    item['comment_date'],
                )
            )
            self.connect.commit()
        except Exception as e:
            print('数据{}出错：{}'.format(item, e))

    def from_sql_get_id(self):
        """
        从数据库中查询已经保存了的user_id,video_id,comment_id进行判断后避免重复保存用户信息
        """
        # 获取保存到数据库中的用户id
        sql_user = "select user_id from mp_user"
        self.cur.execute(sql_user)
        for i in self.cur.fetchall():
            self.save_user_id.append(i[0])

        # 获取保存到数据库中的视频id
        sql_video = "select video_id from mp_video"
        self.cur.execute(sql_video)
        for i in self.cur.fetchall():
            self.save_video_id.append(i[0])

        # 获取保存到数据库中的评论id
        sql_comment = "select comment_id from mp_comment"
        self.cur.execute(sql_comment)
        for i in self.cur.fetchall():
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

        with open('city_code.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(city_code_json, ensure_ascii=False))

    def city_code2city(self, country, province, city):
        """
        将该用户的地区code转换成名称
        :param country: 国家
        :param province: 省份
        :param city: 城市
        :return: 转换后的名称
        """
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

    def main(self):
        """
        调用接口
        """
        if not os.path.exists(r'city_code.json'):
            self.get_city_code()
        else:
            with open(r'city_code.json', 'r', encoding='utf-8') as f:
                self.city_code.update(json.loads(f.read()))
        self.from_sql_get_id()
        self.get_info()


if __name__ == '__main__':
    while True:
        try:
            number = eval(input('请输入视频下载页码：').replace(' ', ''))
        except Exception as e:
            print('请检查输入！')
        else:
            mp = MeiPai(number)
            mp.main()
            break
