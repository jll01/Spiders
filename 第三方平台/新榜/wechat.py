import requests
import re
import random
import hashlib
import os
import json
import time
import string

from dateutil.parser import parse
from fake_useragent import UserAgent
from requests.packages import urllib3
from urllib.parse import quote

import xinbang_login

urllib3.disable_warnings()


class WeChatDetail(object):
    def __init__(self, login_phone, login_passwd, name):
        # 请求的cookie
        self.cookie = ''
        # self.cookie = 'UM_distinctid=177e8d4a2f93b9-03526c0ab4e65a-53e356a-144000-177e8d4a2fa845; __root_domain_v=.newrank.cn; _qddaz=QD.mn5ta6.j8rew4.klp6x2z7; Hm_lvt_a19fd7224d30e3c8a6558dcb38c4beed=1614518985,1614567662; token=6336338AC8944B4C97D7CBFAA244DFA5; CNZZDATA1253878005=261954781-1614569194-https%253A%252F%252Fnewrank.cn%252F%7C1614569194; Hm_lpvt_a19fd7224d30e3c8a6558dcb38c4beed=1614571046; _qdda=2-1.24rm1h; _qddab=2-45o4dq.klq1wx8p; _qddamta_2852150610=2-0'
        # 请求头代理
        self.user_agent = UserAgent(verify_ssl=False).random
        # 保存cookie访问
        self.s = requests.Session()
        # 公众号的名称
        self.wechat_name = name
        # 获取微信号
        self.get_account_url = 'https://www.newrank.cn/xdnphb/data/weixinuser/searchWeixinDataByCondition'
        # 获取粉丝数
        self.get_fans_url = 'https://www.newrank.cn/xdnphb/detail/v1/rank/head/getEstimateFansNum'
        # 获取发文数
        self.get_push_num_url = 'https://www.newrank.cn/xdnphb/detail/v1/rank/article/contentCreation'
        # 获取评论数
        self.get_comment_url = 'https://www.newrank.cn/xdnphb/detail/v1/rank/article/interactiveReview'
        # 获取在看阅读点赞等数据
        self.get_detail_url = 'https://www.newrank.cn/xdnphb/detail/v1/rank/data/rankings'
        self.refer_url = 'https://www.newrank.cn/public/info/search.html?value={}&isBind=false'
        # 详情refer url
        self.detail_refer_url = 'https://www.newrank.cn/new/?account={}'
        # 初始公众号的微信号
        self.account = ''
        # 登陆手机号
        self.login_phone = login_phone
        # 登陆密码
        self.passwd = login_passwd

    @staticmethod
    def get_nonce():
        """
        从num_str中获取9位随机数
        :return:
        """
        num_str = string.digits + string.ascii_lowercase[:6]
        return ''.join(random.sample(num_str, 9))

    def passwd_md5(self):
        """
        登陆密码
        :return:
        """
        m = hashlib.md5(self.passwd.encode('utf-8')).hexdigest() + 'daddy'
        password = hashlib.md5(m.encode('utf-8')).hexdigest()
        return password

    @staticmethod
    def get_token():
        return f'FFFF0N00000000009594:{int(time.time() * 1000)}:{random.random()}'

    def login(self):
        """
        登陆 目前 密码 nonce xyz 参数正确 sig、token、sessionId还不确定怎么加密的
        :return:
        """
        nonce = self.get_nonce()
        pwd = self.passwd_md5()
        # 获取xyz参数的输入值
        scene = "nc_login"
        token = self.get_token()
        # sessionId和sig是阿里云验证码返回的
        sessionId = "01X-4mpiVPEX69gtOfmUgYm1l74aj5f_GipeEpfnqbVD4O5EUIr8j9JZeIP92pHjCR5T51pHj175-TfRUf0ZHDGjyTMPeJ_H9whUO3L3bXcJ-zHWWytiSlkvSVd1WRPv-4SBiVK86TK8mkh3xO-3CjdbKaxnDDr0bs0toJIuL7yRUWSgmj8IffaRekAmYsxaI34NSZrZlUUo2sM9IA_BjoHQ"
        sig = "05XqrtZ0EaFgmmqIQes-s-CO0f3OpdH1G1CCLBwJa_FQjZldcEn6jBZunqSxbEc_CyYah7XK05qVWXPLZmJciRSfmO5pBJiH0Vp7GkOaq-v1AVbtpWo7-V_MRoMEmR-dTOInQGFH6NO6wcZZQRYGx4EgeUvt3HHBoUrUxZNpfwWFxjWErGIjl3P437OG5HYfkBabf-xDoKPRcQAJCLde08uMGZ5JLxUN6mpbrpxm57qTWb1reYey4RRSt_1hH8wcAAh53-VtJ5drUXzQinV1AVPjehKPPNIbTmcjs_Goa5n-FLl3Po800rso5WNAsr7GOTUjTqo0BPnzKGhgT6lWCuwHKjAsTzL2W511gla9PQyDzzI-Eqxtlis0dNocxr64P4WjmcPqzx2nNaZuHL-iYJpWIKfh4tFDEglS2u_VWm8QfA6FMs-iqRW5SixjiYix-8Tunak3dcRqXCHlmX6ZUZcppsJc9QNqzCQlvuzpKRrpU"

        h = f'/nr/user/login/loginByAccount?AppKey=joker&account={self.login_phone}&adeOrMedia=0&password={pwd}&scene={scene}&sessionId={sessionId}&sig={sig}&state=1&token={token}&nonce={nonce}'
        # 获取xyz，md5加密
        xyz = hashlib.md5(h.encode('utf-8')).hexdigest()
        url = 'https://www.newrank.cn/nr/user/login/loginByAccount'
        headers = {
            'origin': 'https://www.newrank.cn',
            'referer': 'https://www.newrank.cn/user/login?back=https%3A//www.newrank.cn/',
            'user-agent': self.user_agent,
        }
        data = {
            'account': self.login_phone,
            'adeOrMedia': '0',
            'password': pwd,
            'scene': scene,
            'sessionId': sessionId,
            'sig': sig,
            'state': '1',
            'token': token,
            'nonce': nonce,
            'xyz': xyz,
        }
        response = self.s.post(url, headers=headers, data=data)
        print(response.text)
        cookies = response.cookies.items()
        cookie = ''
        for name, value in cookies:
            cookie += '{0}={1};'.format(name, value)
        print(cookie)

    def get_wechat_account(self):
        """
        获取公众号的微信号
        @return: 微信号、主体名称
        """
        headers = {
            'User-Agent': self.user_agent,
            'cookie': self.cookie,
            'origin': 'https://www.newrank.cn',
            'referer': self.refer_url.format(quote(self.wechat_name)),
        }
        # 随机数
        nonce = self.get_nonce()
        # 获取xyz参数的输入值
        h = f'/xdnphb/data/weixinuser/searchWeixinDataByCondition?AppKey=joker&filter=&hasDeal=false&keyName={self.wechat_name}&order=relation&nonce={nonce}'
        # 获取xyz，md5加密
        xyz = hashlib.md5(h.encode('utf-8')).hexdigest()
        data = {
            'filter': '',
            'hasDeal': 'false',
            'keyName': self.wechat_name,
            'order': 'relation',
            'nonce': nonce,
            'xyz': xyz,
        }
        # 默认的公众号的微信号、所属公司
        account, certifiedText, name = '', '', ''
        try:
            response = self.s.post(self.get_account_url, headers=headers, data=data, verify=False).json()
            result = response.get('value').get('result')[0]
            account = result.get('account', '')
            certifiedText = result.get('certifiedText', '')
            name = result.get('name', '')
        except:
            pass
        return account, certifiedText, name

    def get_article_fans(self):
        """
        获取公众号的粉丝数
        @return: 粉丝数
        """
        # 随机数
        nonce = self.get_nonce()
        # 获取xyz的输入值
        h = f'/xdnphb/detail/v1/rank/head/getEstimateFansNum?AppKey=joker&account={self.account}&nonce={nonce}'
        # md5加密
        xyz = hashlib.md5(h.encode('utf-8')).hexdigest()

        headers_fans = {
            'User-Agent': self.user_agent,
            'origin': 'https://www.newrank.cn',
            'referer': self.detail_refer_url.format(self.account),
            'cookie': self.cookie
        }
        data_fans = {
            'account': self.account,
            'nonce': nonce,
            'xyz': xyz,
        }
        try:
            response_fans = self.s.post(self.get_fans_url, headers=headers_fans, data=data_fans, verify=False).json()
            fans_num = response_fans.get('value').get('fullAvg_read', '')
            # 先将'1,000' 转换成 '1000' 然后提取数字
            fan = re.findall(r'[0-9.]+', fans_num.replace(',', ''))
            # 转换成整型
            fan_n = eval(fan[0]) if len(fan) >= 1 else 0
            # 将 万 转换成 数字
            if '万' in fans_num:
                fans_num = fan_n * 10000
            else:
                fans_num = fan_n

            return round(fans_num, 2)
        except:
            return 0

    def get_article_num(self):
        """
        获取发文数
        @return: 一个月发文数
        """
        # 9位随机数
        nonce = self.get_nonce()
        # 获取xyz的输入值
        h = f'/xdnphb/detail/v1/rank/article/contentCreation?AppKey=joker&account={self.account}&nonce={nonce}'
        # md5加密获取xyz
        xyz = hashlib.md5(h.encode('utf-8')).hexdigest()

        headers_article_num = {
            'User-Agent': self.user_agent,
            'origin': 'https://www.newrank.cn',
            'referer': self.detail_refer_url.format(self.account),
            'cookie': self.cookie
        }
        data_article_num = {
            'account': self.account,
            'nonce': nonce,
            'xyz': xyz,
        }
        try:
            response_t = self.s.post(self.get_push_num_url, headers=headers_article_num, data=data_article_num, verify=False).json()
            push_num = response_t.get('value').get('oriRate').get('total', 0)
        except:
            push_num = 0

        return push_num

    def get_comment_num(self):
        """
        一个月评论数
        @return:
        """
        # 9位随机数
        nonce = self.get_nonce()
        # 获取xyz的输入值
        h = f'/xdnphb/detail/v1/rank/article/interactiveReview?AppKey=joker&account={self.account}&nonce={nonce}'
        # md5加密xyz
        xyz = hashlib.md5(h.encode('utf-8')).hexdigest()
        headers_comment_num = {
            'User-Agent': self.user_agent,
            'origin': 'https://www.newrank.cn',
            'referer': self.detail_refer_url.format(self.account),
            'cookie': self.cookie
        }
        data_comment = {
            'account': self.account,
            'nonce': nonce,
            'xyz': xyz,
        }
        try:
            response_com = self.s.post(self.get_comment_url, headers=headers_comment_num, data=data_comment, verify=False).json()
            comment_count = response_com.get('value').get('commentCount', 0)
        except:
            comment_count = 0

        return comment_count

    def get_article_detail_num(self):
        """
        获取点赞like_num、在看see_num、阅读read_num
        @return: 阅读、在看、点赞
        """
        # 9位随机数
        nonce = self.get_nonce()
        # xyz的输入值
        h = f'/xdnphb/detail/v1/rank/data/rankings?AppKey=joker&account={self.account}&type=day&nonce={nonce}'
        # md5加密
        xyz = hashlib.md5(h.encode('utf-8')).hexdigest()
        headers_detail_num = {
            'User-Agent': self.user_agent,
            'origin': 'https://www.newrank.cn',
            'referer': self.detail_refer_url.format(self.account),
            'cookie': self.cookie
        }
        data_rank = {
            'account': self.account,
            'type': 'day',
            'nonce': nonce,
            'xyz': xyz,
        }
        # 默认的值
        try:
            response_rank = self.s.post(self.get_detail_url, headers=headers_detail_num, data=data_rank, verify=False).json()
            res_list = response_rank.get('value', [])
            read_list = []
            see_num = []
            like_num = []
            if res_list:
                for i in res_list:
                    read_list.append(int(i.get('max_article_clicks_count', '0')))
                    see_num.append(int(i.get('article_likes_count', '0')))
                    like_num.append(int(i.get('article_pre_like', '0')))
            else:
                read_list = read_list.append(0)
                see_num = see_num.append(0)
                like_num = like_num.append(0)
            read_num = max(read_list)
            see_num = max(see_num)
            like_num = max(like_num)
        except:
            read_num, see_num, like_num = 0, 0, 0

        return read_num, see_num, like_num

    def judge_login(self):
        """
        判断是否存在cookie
        @return:
        """
        # 是否存在保存cookie的文件
        if not os.path.exists(f'xinbang_cookie.json'):
            # 创建浏览器 未登录！
            xinbang_login.main(self.login_phone, self.passwd)
        else:
            # 存在文件的话读取文件内容
            with open(f'xinbang_cookie.json', 'r', encoding='utf-8') as f:
                read_cookie = json.loads(f.read())
                # 判断登陆的时间和当前的时间差，时间太长直接重新获取
                now_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                time_c = parse(now_str) - parse(read_cookie.get('date', now_str))
                # 获取cookie的时间和当前的时间差如果大于阈值，则重新获取cookie
                if time_c.days >= 7 or not read_cookie.get('cookie', ''):
                    xinbang_login.main(self.login_phone, self.passwd)
                else:
                    # 满足条件的话获取cookie
                    self.cookie = read_cookie.get('cookie')

    def main(self):
        # 登陆 阿里云滑动验证码
        # self.login()
        self.judge_login()
        # 获取公众号对应的微信号、主体
        self.account, company_name, nick_name = self.get_wechat_account()
        # 默认的返回值
        result = {}
        # 如果存在微信号
        if self.account:
            # 关注量
            fans_num = self.get_article_fans()
            # 发文数
            push_num = self.get_article_num()
            # 评论数
            comment_num = self.get_comment_num()
            # 阅读、在看、点赞
            read_num, see_num, like_num = self.get_article_detail_num()
            if nick_name.startswith('@font'):
                nick_name = nick_name[5:]

            if nick_name.endswith('#font'):
                nick_name = nick_name[:-5]
            result['name'] = nick_name
            result['account'] = self.account
            result['company_name'] = company_name[5:] if company_name else ''

            result['fans_num'] = fans_num
            result['push_num'] = push_num
            result['read_num'] = read_num
            result['like_num'] = like_num
            result['comment_num'] = comment_num
            result['see_num'] = see_num
        return result


if __name__ == '__main__':
    phone = '****'
    passwd = '****'
    w_name = '****'

    print(WeChatDetail(phone, passwd, w_name).main())
