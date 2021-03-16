import requests
import json
import datetime
import time
import os
import xinbang_login
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from fake_useragent import UserAgent
from requests.packages import urllib3


urllib3.disable_warnings()


class DouYin(object):
    def __init__(self, phone, passwd, nick_or_id):
        self.phone = phone
        self.passwd = passwd
        self.user_agent = UserAgent(verify_ssl=False).random
        self.n_token = '9116298d52d64bbfb2bafa92267f74f2'
        # 抖音昵称或者抖音号
        self.nick_or_id = nick_or_id
        self.uid = ''
        self.cookie = ''

    def get_account(self):
        """
        根据抖音昵称或者抖音号获取uid和其他账号信息
        @return: 账号主体的uid、性别、昵称、城市等
        """
        # 请求数据的url
        url = 'https://gw.newrank.cn/api/xd/xdnphb/nr/cloud/douyin/accountSearch'
        headers = {
            'cookie': self.cookie,
            'n-token': self.n_token,
            'origin': 'https://xd.newrank.cn',
            'referer': 'https://xd.newrank.cn/tiktok/account',
            'user-agent': self.user_agent,
            'content-type': 'application/json;charset=UTF-8'
        }
        data = {
            "input": {
                "keyword": self.nick_or_id,
                "type": ""
            },
            "xd_tags": [],
            "type": "",
            "nr_range_list": [],
            "verify": "",
            "contact": "",
            "mcn": "",
            "with_fusion_shop_entry": "",
            "is_live": "",
            "account_info": {
                "province": "",
                "city": "",
                "gender": "",
                "constellation_name": "",
                "age_range": ""
            },
            "data_performance": {
                "favorited_range_list": [],
                "follower_range_list": []
            },
            "relate_goods": {
                "goods_name": "",
                "goods_cate1": "",
                "goods_cate2": "",
                "price_range": "",
                "goods_sales_range": "",
                "visitor_count_range": "",
                "goods_source": "",
                "price": {
                    "gte": "",
                    "lt": ""
                }
            },
            "fans_info": {
                "province": "",
                "city": "",
                "gender": "",
                "age_range": "",
                "constellation_name": ""
            },
            "sort": "",
            "size": 20,
            "start": 1,
            "is_claim": ""
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers, verify=False, timeout=30).json()
            datas = response.get('data').get('list')[0]
            item = dict()
            item['account'] = datas.get('account', '')
            item['province'] = datas.get('province', '')
            item['city'] = datas.get('city', '')
            item['gender'] = datas.get('gender', '')
            item['nickname'] = datas.get('nickname', '')
            item['uid'] = datas.get('uid', '')
            # 30天内直播数量
            item['webcast_count_30'] = self.str2num(datas.get('webcast_count_30', '0'))
            return item, item['uid']
        except Exception as e:
            print(e)
            return {}, ''

    def get_account_two(self):
        url = 'https://gw.newrank.cn/api/xd/xdnphb/nr/cloud/douyin/DOU/search/getSuggestAccountDTO'
        data = {
            'keyword': self.nick_or_id,
            'key': "account",
        }
        headers = {
            'cookie': self.cookie,
            'n-token': self.n_token,
            'origin': 'https://xd.newrank.cn',
            'referer': 'https://xd.newrank.cn/tiktok/account',
            'user-agent': self.user_agent,
            'content-type': 'application/json;charset=UTF-8'
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers, verify=False, timeout=30).json()
            datas = response.get('data')[0]
            item = dict()
            item['nickname'] = datas.get('nickname', '')
            item['uid'] = datas.get('uid', '')
            item['account'] = datas.get('short_id', '')
            if not item['account'] or item['account'] == '0':
                item['account'] = datas.get('unique_id', '')
            # item['webcast_count_30'] = datas.get('webcast_count_30', '0')
            return item, item['uid']
        except:
            return {}, ''

    def get_one_month_add(self):
        """
        根据uid获取当前账号的粉丝、点赞、视频数量
        @return:
        """
        url = 'https://gw.newrank.cn/api/xd/xdnphb/nr/cloud/douyin/detail/trend'
        collection_time = (datetime.datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            "uid": self.uid,
            # "collection_time": "2020-03-25 17:33:50",
            # "collection_time": collection_time,
        }
        headers_data = {
            'cookie': self.cookie,
            'n-token': self.n_token,
            'origin': 'https://xd.newrank.cn',
            'referer': f'https://xd.newrank.cn/tiktok/detail/latest/{self.uid}',
            'user-agent': self.user_agent,
            'content-type': 'application/json;charset=UTF-8',
        }
        try:
            response_data = requests.post(url, data=json.dumps(data), headers=headers_data, verify=False, timeout=30)
            datas = response_data.json().get('data')
            detail = dict()
            # 视频新增数量
            add_video_num_list = []
            # 粉丝数增加
            add_mplatform_followers_count_list = []
            # 点赞数增加
            add_total_favorited_list = []
            for data in datas:
                add_video_num_list.append(self.str2num(data.get('aweme_count_today', '0')))
                add_mplatform_followers_count_list.append(self.str2num(data.get('add_mplatform_followers_count', '0')))
                add_total_favorited_list.append(self.str2num(data.get('add_total_favorited', '0')))

            detail['like_num'] = self.str2num(datas[-1].get('total_favorited', '0'))
            detail['fans_num'] = self.str2num(datas[-1].get('mplatform_followers_count', '0'))
            detail['video_num'] = self.str2num(datas[-1].get('aweme_count', '0'))
            # 新增视频的数量
            detail['add_video_num'] = sum(add_video_num_list)
            # 新增点赞数
            detail['add_like_num'] = sum(add_total_favorited_list)
            # 新增粉丝数
            detail['add_fans_num'] = sum(add_mplatform_followers_count_list)
            return detail
        except Exception as e:
            print(e)
            return {}

    def get_live_count(self):
        """
        直播带货数据
        @return:
        """
        url = 'https://gw.newrank.cn/api/xd/xdnphb/nr/cloud/douyin/webcast/webcastList'
        headers_data = {
            'cookie': self.cookie,
            'n-token': self.n_token,
            'origin': 'https://xd.newrank.cn',
            'referer': f'https://xd.newrank.cn/tiktok/detail/latest/{self.uid}',
            'user-agent': self.user_agent,
            'content-type': 'application/json;charset=UTF-8',
        }
        data = {
            "date_type": "",
            "size": 20,
            "sort": "",
            "start": 1,
            "has_commerce_goods": "",
            "uid": self.uid,
        }
        try:
            response_data = requests.post(url, data=json.dumps(data), headers=headers_data, verify=False, timeout=30).json()
            live_count = response_data.get('data').get('count')
        except:
            live_count = 0
        return {'live_count': live_count}

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
        if not self.cookie:
            return {}
        # 第一种有次数限制
        # return_data, self.uid = self.get_account()
        # 目前没有次数限制
        return_data, self.uid = self.get_account_two()
        if self.uid:
            return_data_detail = self.get_one_month_add()
            return_data_live = self.get_live_count()
            return_data.update(return_data_detail)
            return_data.update(return_data_live)
        else:
            return_data = {}
        return return_data


if __name__ == '__main__':
    login_phone = '****'
    login_passwd = '****'
    nickname = ''
    dy = DouYin(login_phone, login_passwd, nickname)
    print(dy.main())
