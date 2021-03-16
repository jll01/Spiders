import requests
import json
import time
import os
import random
import hashlib
import xinbang_login
import string

from dateutil.parser import parse
from fake_useragent import UserAgent
from requests.packages import urllib3


urllib3.disable_warnings()


class Kuaishou(object):
    """
    新快 快手号
    """
    def __init__(self, phone, passwd, nick_or_id):
        self.phone = phone
        self.passwd = passwd
        self.user_agent = UserAgent(verify_ssl=False).random
        # 快手昵称或者快手号
        self.nick_or_id = nick_or_id
        self.uid = ''
        self.cookie = ''

    @staticmethod
    def get_nonce():
        """
        从num_str中获取9位随机数
        :return:
        """
        num_str = string.digits + string.ascii_lowercase[:6]
        return ''.join(random.sample(num_str, 9))

    @staticmethod
    def get_xyz(_url):
        return hashlib.md5(_url.encode('utf-8')).hexdigest()

    def get_account(self):
        """
        根据抖音昵称或者抖音号获取uid和其他账号信息
        @return: 账号主体的uid、性别、昵称、城市等
        """
        # 请求数据的url
        url = 'https://xk.newrank.cn/xdnphb/nr/cloud/ks/account/accountSearch'
        headers = {
            'cookie': self.cookie,
            'origin': 'https://xk.newrank.cn',
            'referer': 'https://xk.newrank.cn/data/account/search',
            'user-agent': self.user_agent,
            'content-type': 'application/json;charset=UTF-8'
        }
        data = {
            "input": {
                "keyword": nickname,
                "type": "all"
            },
            "verifyType": [],
            "contact": "",
            "withFusionShopEntry": "",
            "maxUserSex": "",
            "accountInfo": {
                "province": "",
                "city": "",
                "ageRange": [],
                "userSex": "",
                "constellationName": []
            },
            "dataPerformance": {
                "fanRange": [],
                "newrankIndexRange": [],
                "avgLike30Range": [],
                "avgComment30Range": [],
                "avgView30Range": []
            },
            "contentTags": [],
            "hasLive": "",
            "sort": "",
            "size": 20,
            "start": 1,
            "type": []
        }
        try:
            nonce = self.get_nonce()
            xyz = self.get_xyz(url + '?AppKey=joker&nonce={}'.format(nonce))
            url = f'{url}?xyz={xyz}&nonce={nonce}'
            response = requests.post(url, data=json.dumps(data), headers=headers, verify=False, timeout=30).json()
            datas = response.get('data').get('list')[0]
            item = dict()
            item['fans'] = datas.get('ownerCount').get('fan', 0)
            item['video_num'] = datas.get('ownerCount').get('photo', 0)
            item['province'] = datas.get('profile').get('province', 0)
            item['city'] = datas.get('profile').get('city', '')
            item['nickname'] = datas.get('profile').get('userName', '')
            item['gender'] = datas.get('profile').get('userSex', '')
            item['userId'] = datas.get('userId', '')
            return item, item['userId']
        except Exception as e:
            return {}, ''

    @staticmethod
    def str2num(str_n):
        """
        字符串数字转换成数字
        @param str_n:
        @return:
        """
        try:
            return eval(str_n)
        except:
            return 0

    def get_cookie_n_token(self):
        # 是否存在保存cookie的文件
        if not os.path.exists('xinbang_cookie.json'):
            # 创建浏览器 未登录！
            xinbang_login.main(self.phone, self.passwd)
        else:
            # 存在文件的话读取文件内容
            with open('xinbang_cookie.json', 'r', encoding='utf-8') as f:
                read_cookie = json.loads(f.read())
                # 根据是否是代理获取对应的ip和port
                # 判断登陆的时间和当前的时间差，时间太长直接重新获取
                now_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                time_c = parse(now_str) - parse(read_cookie.get('date', now_str))
                # 获取cookie的时间和当前的时间差如果大于阈值，则重新获取cookie
                if time_c.days >= 7:
                    xinbang_login.main(self.phone, self.passwd)
                else:
                    # 满足条件的话获取cookie
                    self.cookie = read_cookie.get('cookie')

    def main(self):
        self.get_cookie_n_token()
        # 第一种有次数限制
        return_data, self.uid = self.get_account()
        print(return_data)


if __name__ == '__main__':
    login_phone = ''
    login_passwd = ''
    nickname = ''
    dy = Kuaishou(login_phone, login_passwd, nickname)
    dy.main()
