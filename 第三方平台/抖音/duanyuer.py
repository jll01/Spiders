import requests
import time
import json

from fake_useragent import UserAgent
from requests.packages import urllib3


class DuanYuer(object):
    def __init__(self, nick_name):
        self.search_url = 'https://xcx.meizhuahuyu.com/douyin/user/getUser?token=f81268ed595352387210d69325eecefb&toPageCode=15'
        self.nick_name = nick_name

    @staticmethod
    def get_d1():
        return 56 * int(time.time() / 10)

    @staticmethod
    def get_d2to5(d1_value, int_value):
        n = str(d1_value)
        r = f'{n[0]}{n[3:]}'
        return str(int(r) * int_value)[:len(n)]

    def get_uid(self):
        data = {
            "nickname": self.nick_name,
            "page": 1
        }
        d1 = self.get_d1()
        d2 = self.get_d2to5(d1, 314)
        d3 = self.get_d2to5(d1, 128)
        d4 = self.get_d2to5(d1, 435)
        d5 = self.get_d2to5(d1, 219)

        headers = {
            'origin': 'https://www.duanyuer.com',
            'referer': 'https://www.duanyuer.com/',
            'user-agent': UserAgent(verify_ssl=False).random,
            'Content-Type': 'application/json;charset=UTF-8',
            'd1': str(d1),
            'd2': d2,
            'd3': d3,
            'd4': d4,
            'd5': d5,
        }
        print(headers)
        response = requests.post(self.search_url, headers=headers, data=json.dumps(data), verify=False).text
        print(response)

    def main(self):
        self.get_uid()


if __name__ == '__main__':
    nick = ''
    urllib3.disable_warnings()
    DuanYuer(nick).main()
