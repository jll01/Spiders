import requests
import time
import json
import random
import urllib3

from fake_useragent import UserAgent


class ITJuZi(object):
    def __init__(self, account, password):
        # 登陆url
        self.login_url = '''https://www.itjuzi.com/api/authorizations'''
        # 事件url
        self.request_url = '''https://www.itjuzi.com/api/investevents'''
        # 总数
        self.pagetotal = 0
        # 页码
        self.page_num = 1
        # 打开json文件
        self.file = open('IT桔子.json', 'a', encoding='utf-8')
        # token，验证用户时候登陆
        self.token = ''
        # 登陆用户名
        self.account = account
        # 登陆密码
        self.password = password

    def login_itjuzi(self):
        """
        登陆IT桔子
        :return: token，验证用户是否登陆
        """
        data_post = {
            "account": self.account,
            "password": self.password,
            "type": "pswd"
        }
        headers = {
            'Origin': 'https://www.itjuzi.com',
            'Host': 'www.itjuzi.com',
            'User-Agent': UserAgent(verify_ssl=False).random
        }

        verify_login = requests.post(self.login_url, data=data_post, headers=headers, verify=False)
        if verify_login.status_code == 200:
            verify_login = verify_login.json()
            return verify_login['data']['token']
        else:
            return ''

    def get_data(self):
        """
        获取事件json数据
        :return:
        """
        while True:
            headers = {
                'cookie': 'Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1592639887; _ga=GA1.2.423241089.1592639889; _gid=GA1.2.1735206124.1592639889; juzi_user=684879; juzi_token=bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3Lml0anV6aS5jb21cL2FwaVwvYXV0aG9yaXphdGlvbnMiLCJpYXQiOjE1OTI2NDAxMTksImV4cCI6MTU5MjY0MzcxOSwibmJmIjoxNTkyNjQwMTE5LCJqdGkiOiJydjZsUlpobnU5WkpNR1B0Iiwic3ViIjo2ODQ4NzksInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjciLCJ1dWlkIjoiTURNRzJoIn0.JxpQw3q5OKb8hetn1KJNnhALs23H48C2NyjbFjaGwP0; Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89=1592640119',
                'origin': 'https://www.itjuzi.com',
                'referer': 'https://www.itjuzi.com/investevent',
                'user-agent': UserAgent(verify_ssl=False).random,
                'authorization': self.token
            }
            # post数据
            post_data = {
                # 总条数
                "pagetotal": self.pagetotal,
                "total": 0,
                "per_page": 20,
                # 请求页码数
                "page": self.page_num,
                "type": 1,
                "scope": "",
                "sub_scope": "",
                "round": [],
                "valuation": [],
                "valuations": "",
                "ipo_platform": "",
                "equity_ratio": "",
                "status": "",
                "prov": "",
                "city": [],
                "time": [],
                "selected": "",
                "location": "",
                "hot_city": "",
                "currency": [],
                "keyword": ""
            }
            item = {}
            try:
                datas_get = requests.post(self.request_url, headers=headers, data=post_data, verify=False)
                datas = datas_get.json()
                data_jsons = datas['data']['data']
                for data in data_jsons:
                    item['id'] = data['id']
                    item['com_id'] = data['com_id']
                    # 日期
                    item['date'] = data['agg_time']
                    # 公司名称
                    item['name'] = data['name']
                    item['logo'] = data['logo']
                    # 行业
                    item['com_scope'] = data['com_scope']
                    # 分类
                    item['com_sub_scope'] = data['com_sub_scope']
                    # 轮次
                    item['round'] = data['round']
                    # 金额
                    item['money'] = data['money']
                    # 最新估值(估算)
                    item['valuation'] = data['valuation'] * 10000
                    # 地区
                    item['prov'] = data['prov'] + data['city']
                    # 注册公司名
                    item['com_registered_name'] = data['com_registered_name']
                    # 公司描述
                    item['com_des'] = data['com_des']
                    # 投资者
                    investors = data['investor']
                    investor_list = []
                    for investor in investors:
                        investor_list.append(investor['name'])
                    item['investors'] = '|'.join(investor_list)

                    print(item)
                    self.save_json(item)

            except Exception as e:
                print(f'请求退出！{e}  {datas}')
                break
            else:
                if datas_get.status_code == 200:
                    self.pagetotal = datas['data']['page']['total']
                    self.page_num += 1
                    time.sleep(random.uniform(1, 3))
                else:
                    time.sleep(1)
                    self.file.close()
                    break

    def save_json(self, item):
        """
        保存json到本地
        :param item: 要保存的数据
        :return:
        """
        self.file.write(json.dumps(item, ensure_ascii=False) + '\n')

    def main(self):
        self.token = self.login_itjuzi()
        if self.token:
            print('登陆成功！')
            self.get_data()
        else:
            print('登陆失败！')


if __name__ == '__main__':
    urllib3.disable_warnings()

    phone = input('请输入用户登陆名(手机号)：')
    passwd = input('请输入密码：')

    it = ITJuZi(phone, passwd)
    it.main()
