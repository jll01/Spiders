import requests
import time
import json
import datetime

from dateutil.relativedelta import relativedelta
from fake_useragent import UserAgent
from requests.packages import urllib3
from requests.adapters import HTTPAdapter


urllib3.disable_warnings()


class ChanMama(object):
    def __init__(self, phone, passwd, search_word):
        self.keyword = search_word
        self.session = requests.Session()
        self.session.keep_alive = False
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.user_agent = UserAgent(verify_ssl=False).random
        self.cookie = ''
        self.phone = phone
        self.passwd = passwd

    def search_user_id(self):
        """
        获取抖音账号对应的uid
        @return: uid、昵称、粉丝数等
        """
        url = 'https://api-service.chanmama.com/v1/home/author/search'
        headers = {
            'Cookie': self.cookie,
            'Host': 'api-service.chanmama.com',
            'Origin': 'https://www.chanmama.com',
            'Referer': f'https://www.chanmama.com/bloggerRank?keyword={self.keyword}',
            'User-Agent': self.user_agent,
        }
        params = {
            'page': '1',
            'star_category': '',
            'star_sub_category': '',
            'product_category': '',
            'keyword': self.keyword,
            'gender': '-1',
            'age': '',
            'fans_gender': '-1',
            'fans_age': '',
            'follower_count': '',
            'product_platform': '',
            'province': '',
            'fans_province': '',
            'contact': '0',
            'is_commerce': '0',
            'is_live': '0',
            'is_sell_live': '0',
            'is_star_author': '0',
            'verification_type': '0',
            'sort': 'follower_count',
            'order_by': 'desc',
            'size': '40',
        }
        try:
            response = self.session.get(url, headers=headers, params=params, verify=False, timeout=10).json()
            if response.get('errCode') == 40006:
                self.login()
                self.main()
            else:
                datas = response.get('data').get('list')[0]
                item = dict()
                item['uuid'] = datas.get('author_id')
                # 昵称
                item['nickname'] = datas.get('nickname')
                # 粉丝
                item['follower_count'] = datas.get('follower_count')
                return item
        except:
            return {}

    def get_detail(self, uuid):
        """
        获取点赞和视频短视频总数
        @param uuid: 唯一标识
        @return: 省、市、点赞、短视频数量等
        """
        url = f'https://api-service.chanmama.com/v1/author/detail/info?author_id={uuid}'
        headers = {
            'Cookie': self.cookie,
            'Host': 'api-service.chanmama.com',
            'Origin': 'https://www.chanmama.com',
            'Referer': f'https://www.chanmama.com/authorDetail/{uuid}',
            'User-Agent': self.user_agent,
        }
        try:
            response = self.session.get(url, headers=headers, verify=False, timeout=10).json()
            datas = response.get('data')
            detail = dict()
            detail['province'] = datas.get('province')
            detail['city'] = datas.get('city')
            detail['total_favorited'] = datas.get('total_favorited')
            detail['aweme_count'] = datas.get('aweme_count')
            return detail
        except:
            return {}

    def get_video_add(self, uuid):
        """
        获取短视频新增数量
        @param uuid:
        @return:
        """
        # 获取现在的时间和一个月前的日期
        now_date = datetime.datetime.today()
        end = f'{now_date.year}-{str(now_date.month).zfill(2)}-{str(now_date.day).zfill(2)}'
        # 上个月的日期，也是查询的开始日期
        last_month = now_date - relativedelta(days=30)
        start = f'{last_month.year}-{str(last_month.month).zfill(2)}-{str(last_month.day).zfill(2)}'
        url = f'https://api-service.chanmama.com/v1/author/detail/awemeAnalysis?author_id={uuid}&start_date={start}&end_date={end}'
        headers = {
            'Cookie': self.cookie,
            'Host': 'api-service.chanmama.com',
            'Origin': 'https://www.chanmama.com',
            'Referer': f'https://www.chanmama.com/authorDetail/{uuid}/aweme',
            'User-Agent': self.user_agent,
        }
        try:
            response = self.session.get(url, headers=headers, verify=False, timeout=10).json()
            video_add = response.get('data').get('summary').get('aweme_count', 0)
            return video_add
        except:
            return 0

    def goods_num(self, uuid):
        """
        获取直播带货的数量
        @param uuid: 请求必须的唯一标识
        @return: 带货数量
        """
        url = f'https://api-service.chanmama.com/v1/author/detail/businessOverview?author_id={uuid}'
        headers = {
            'Cookie': self.cookie,
            'Host': 'api-service.chanmama.com',
            'Origin': 'https://www.chanmama.com',
            'Referer': f'https://www.chanmama.com/authorDetail/{uuid}',
            'User-Agent': self.user_agent,
        }
        try:
            response = self.session.get(url, headers=headers, verify=False, timeout=10).json()
            goods_count = response.get('data').get('total_product_count', 0)
            return goods_count
        except:
            return 0

    def login(self):
        """
        登陆禅妈妈
        @return:
        """
        url = 'https://api-service.chanmama.com/v1/access/token'
        headers = {
            'Host': 'api-service.chanmama.com',
            'Origin': 'https://www.chanmama.com',
            'Referer': 'https://www.chanmama.com/login',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }
        data = {
            'appId': '10000',
            'password': self.passwd,
            'timeStamp': int(time.time()),
            'username': self.phone,
        }
        try:
            response = self.session.post(url, headers=headers, data=json.dumps(data), verify=False, timeout=10)
            cookies = response.cookies.items()
            cookie = ''
            for name, value in cookies:
                cookie += '{0}={1}'.format(name, value)
            self.cookie = cookie
        except:
            pass

    def main(self):
        return_data = {}
        self.login()
        if not self.cookie:
            return return_data

        res = self.search_user_id()
        if res:
            uuid = res.get('uuid')
            detail = self.get_detail(uuid)
            video_add = self.get_video_add(uuid)
            goods_count = self.goods_num(uuid)
            res.update(detail)
            res.update({
                'video_add': video_add,
                'goods_num': goods_count,
            })
            return_data = {
                'fans': res.get('follower_count', 0),
                'video_added': res.get('video_add', 0),
                'bring_goods': res.get('goods_num', 0),
                'highest_like': res.get('total_favorited', 0)
            }
        else:
            pass
        return return_data


if __name__ == '__main__':
    login_phone = ''
    login_passwd = ''
    key_word = ''
    cmm = ChanMama(login_phone, login_passwd, key_word)
    cmm.main()
