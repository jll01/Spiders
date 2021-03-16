import requests
import json
import time
import datetime
import random

from fake_useragent import UserAgent
from dateutil.relativedelta import relativedelta


class HuiTun(object):
    def __init__(self, phone, passwd, keyword):
        """
        灰豚数据
        @param phone: 登录手机号
        @param passwd: 登录密码
        @param keyword: 搜索关键词
        """
        self.user_agent = UserAgent(verify_ssl=False).random
        self.phone = phone
        self.passwd = passwd
        self.keyword = keyword
        self.cookie = ''

    def login_huitun(self):
        """
        登陆灰豚数据
        @return: 登录后的cookie值
        """
        login_url_first = 'https://login.huitun.com/weChat/userLogin'
        headers_first = {
            'Content-Type': 'application/json',
            'Host': 'login.huitun.com',
            'Origin': 'https://dy.huitun.com',
            'User-Agent': self.user_agent,
        }
        data = {
            'mobile': self.phone,
            'password': self.passwd,
        }
        requests.post(login_url_first, headers=headers_first, data=json.dumps(data))

        headers_second = {
            'Content-Type': 'application/json',
            'Origin': 'https://dy.huitun.com',
            'User-Agent': self.user_agent,
        }
        login_url_second = f'https://dyapi.huitun.com/userLogin?_t={int(time.time() * 1000)}'
        res = requests.post(login_url_second, headers=headers_second, data=json.dumps(data))
        cookies = res.cookies.items()
        cookie = ''
        for name, value in cookies:
            cookie += '{0}={1}'.format(name, value)
        self.cookie = cookie

    def search_live_user(self):
        """
        搜索用户，获取uid(必须)、点赞等数据
        @return: 获取到的数据
        """
        search_url = 'https://dyapi.huitun.com/search/user'
        headers = {
            'Cookie': self.cookie,
            'Host': 'dyapi.huitun.com',
            'Origin': 'https://dy.huitun.com',
            'User-Agent': self.user_agent,
        }
        params = {
            '_t': int(time.time() * 1000),
            'cids': '',
            'tagList': '',
            'followerRange': '',
            'diggRange': '',
            'ageRange': '',
            'scoreRange': '',
            'gender': '',
            'province': '',
            'region': '',
            'maxGender': '',
            'maxAge': '',
            'maxArea': '',
            'maxCity': '',
            'customVerify': '',
            'verify': 'false',
            'blueV': 'false',
            'mcn': 'false',
            'fusionShopEnter': 'false',
            'promotionUser': 'false',
            'contact': 'false',
            'goodsSource': '',
            'sales': '',
            'visitorRange': '',
            'prices': '',
            'goodsKeyword': '',
            'keywordMatch': '',
            'goodsCates': '',
            'subIds': '',
            'leafIds': '',
            'keyword': self.keyword,
            'from': '1',
            'sortField': '',
            'tag': '0',
            'fusionShopFlag': 'false',
        }
        try:
            response = requests.get(search_url, headers=headers, params=params)
            if response.status_code != 200:
                self.login_huitun()
                response = requests.get(search_url, headers=headers, params=params)

            datas = response.json().get('data')[0]
            item = dict()
            item['uid'] = datas.get('uid', '')
            item['nickname'] = datas.get('nickname', '')
            item['douyin_id'] = datas.get('authorId', '')
            item['fans_count'] = datas.get('followerCountTotal', '')
            item['like_count'] = datas.get('totalFavorited', '')
            item['video_count'] = datas.get('awemeCount', '')
            return item
        except:
            return {}

    def get_fans_add(self, uid):
        """
        获取粉丝增加数量
        @param uid: 唯一标识
        @return:
        """
        fans_add_url = 'https://dyapi.huitun.com/user/detail'
        headers = {
            'Cookie': self.cookie,
            'Host': 'dyapi.huitun.com',
            'Origin': 'https://dy.huitun.com',
            'User-Agent': self.user_agent,
        }
        params = {
            '_t': int(time.time() * 1000),
            'uid': uid,
            'example': uid,
        }
        try:
            response = requests.get(fans_add_url, headers=headers, params=params).json()
            datas_fan = response.get('data')
            video_added = datas_fan.get('awewe30Count', 0)
            return video_added
        except:
            return 0

    def get_goods_num(self, uid):
        """
        获取直播带货数据
        @param uid: 唯一标识
        @return:
        """
        goods_url = 'https://dyapi.huitun.com/live/record'
        headers = {
            'Cookie': self.cookie,
            'Host': 'dyapi.huitun.com',
            'Origin': 'https://dy.huitun.com',
            'User-Agent': self.user_agent,
        }
        page_num = 1
        now_date = datetime.datetime.today()
        end = f'{now_date.year}-{now_date.month}-{now_date.day}'
        last_month = now_date - relativedelta(months=1)
        start = f'{last_month.year}-{last_month.month}-{last_month.day}'
        goods_num = 0
        while True:
            params = {
                '_t': int(time.time() * 1000),
                'from': page_num,
                'time': '',
                'has': 'HAS_GOODS',
                'keyword': '',
                'mod': 'DESC',
                'sort': '',
                'start': start,
                'end': end,
                'filterMap': '',
                'uid': uid,
                'example': uid,
            }
            try:
                response = requests.get(goods_url, headers=headers, params=params).json()
                datas = response.get('data')
                # 数据为空的时候退出循环
                if not datas:
                    return goods_num

                for i in datas:
                    goods_num += i.get('goodsNum', 0)
                page_num += 1
                time.sleep(random.uniform(1, 3))
            except:
                return goods_num

    def main(self):
        self.login_huitun()
        if not self.cookie:
            return {}
        res = self.search_live_user()
        uid = res.get('uid', 0)
        if uid:
            video_add = self.get_fans_add(uid)
            bring_goods = self.get_goods_num(uid)
            res.update({
                'video_added': video_add,
                'bring_goods': bring_goods,
            })
        return res


if __name__ == '__main__':
    login_phone = ''
    login_passwd = ''
    keyword_search = ''
    print(HuiTun(login_phone, login_passwd, keyword_search).main())
