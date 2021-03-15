import requests
import re
import time
import os
import socket
import json
import cpca

from selenium import webdriver
from fake_useragent import UserAgent
from dateutil.parser import parse


class QCC(object):
    def __init__(self, company_name):
        # 首页
        self.qcc_url = 'https://www.qcc.com/'
        # 根据公司名称获取url
        self.get_company_url_url = 'https://m.qcc.com/search?key={}'
        # 查找电话和邮箱
        self.tel_url = 'https://m.qcc.com/firm/{}.html'
        # 获取公司基本信息(工商和变更)
        self.base_url = 'https://www.qcc.com/cbase/{}'
        # 搜索关键词
        self.search_key = company_name
        self.cookie = ''
        # 公司的唯一标识
        self.cbase = ''
        self.cookie_name = f'qcc_browser_cookie.json'

    def et_driver(self):
        """
        创建浏览器获取cookie
        @return:
        """
        print('正在创建模拟浏览器，请稍后！')
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        # 防止服务器识别是模拟登陆
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option("useAutomationExtension", False)
        # 谷歌driver
        driver = webdriver.Chrome(executable_path='../driver/chromedriver.exe', options=options)
        # 浏览器窗口最大化
        driver.maximize_window()
        # 防止服务器识别是模拟登陆(新版)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            """
        })
        driver.delete_all_cookies()
        print('创建完成！')
        driver.get(self.qcc_url)
        time.sleep(1)
        cookies = driver.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        cookie = [f'{item[0]}={item[1]}' for item in cookie_dict.items()]
        cookie = '; '.join(cookie)
        with open(f'./save_cookie/{self.cookie_name}', 'w', encoding='utf-8') as f:
            ip_port = f'{socket.gethostbyname(socket.gethostname())}:{"0000"}'
            cookie_data = {ip_port: [
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                cookie
            ]}
            f.write(json.dumps(cookie_data, ensure_ascii=False))
        driver.quit()
        return cookie

    def get_company_url(self):
        """
        获取公司详情的url
        @return: 获取到的公司请求的参数
        """
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random,
            'Cookie': self.cookie
        }
        try:
            response = requests.get(self.get_company_url_url.format(f'{self.search_key}'), headers=headers, timeout=20)
            if '小查未找到数据' in response.text:
                return '01'
            else:
                all_cbase = re.findall(r'/firm/(\w+).html', response.text, re.DOTALL)
                return self.join_list(all_cbase)
        except:
            return ''

    @staticmethod
    def join_list(in_list):
        """
        拼接列表
        @param in_list:
        @return:
        """
        if len(in_list) >= 1:
            return in_list[0]
        else:
            return ''

    @staticmethod
    def money(mo):
        """
        分离钱和币种
        @param mo: 获取到的公司注册资金
        @return: 数字，币种(100000, 人民币)
        """
        change_value = {
            '元': '人民币',
            '元人民币': '人民币',
        }
        if not mo or mo.strip() == '-':
            register_capital = '-'
            register_currency = '人民币'
        else:
            s = mo.replace(',', '').replace('(', '').replace(')', '')
            try:
                if '万' in s:
                    value = s.split('万')
                else:
                    value = re.findall(r'(\d+)(\w+)', s)[0]
            except:
                value = [0, '人民币']
            register_capital = int(eval(value[0]) * 10000)
            register_currency = change_value.get(value[1], value[1])

        return register_capital, register_currency

    def get_tel_mail(self):
        """
        获取电话和邮箱
        @return: 电话和邮箱
        """
        if not self.cbase:
            return '', ''

        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random,
            'Cookie': self.cookie
        }
        try:
            response = requests.get(self.tel_url.format(self.cbase), headers=headers)
            con = response.text
            tel = self.join_list(re.findall(r'class="phone\s?a-decoration">(.*?)</a>', con, re.DOTALL))
            email = self.join_list(re.findall(r'class="email\s?a-decoration">(.*?)</a>', con, re.DOTALL))
            address = self.join_list(re.findall(r'<div\s?class="address">(.*?)</div>', con, re.DOTALL)).strip()
            return tel, email, address
        except:
            return '', '', ''

    def get_base_info(self, phone, email, address):
        """
        获取其他工商信息和变更信息
        @return: 获取到的工商信息和变更信息
        """
        item = {}

        # 如果获取到的参数为空直接返回
        if not self.cbase:
            return {}

        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random,
            'Cookie': self.cookie
        }
        try:
            response = requests.get(self.base_url.format(self.cbase), headers=headers)
            con = response.text
            # 公司名称
            item['company_name'] = self.merge_list(re.findall(r'<h1>(.*?)</h1>', con))
            # 法定代表人
            item['legal'] = ''.join(re.findall(r"class=[\"']bname[\"']>\s?<h2\s?class=.*?>(.*?)</h2>", con, re.DOTALL)).strip()
            # 电话
            item['phone'] = phone
            # 邮箱
            item['email'] = email
            # 状态
            item['register_status'] = self.merge_list(re.findall(r"class=[\"']tb[\"']>\s?登记状态\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL))
            # 企业官网
            item['official_url'] = self.merge_list(re.findall(r"onclick=[\"']zhugeTrack\([\"']企业主页-查看官网[\"'],{[\"']企业名称':'\w+'}\);[\"']\s?href=[\"'](.*?)[\"']", con, re.DOTALL)).strip()
            # 注册资本，币种
            item['register_capital'], item['register_currency'] = self.money(''.join(re.findall(r"class=[\"']tb[\"']>\s?注册资本\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip())
            # 实缴资本，币种
            item['real_capital'], item['real_currency'] = self.money(''.join(re.findall(r"class=[\"']tb[\"']>\s?实缴资本\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip())
            # 统一社会信用代码
            item['credit_code'] = self.merge_list(re.findall(r"class=[\"']tb[\"']>\s?统一社会信用代码\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip()
            # 工商注册号
            item['business_number'] = self.merge_list(re.findall(r"class=[\"']tb[\"']>\s?工商注册号\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip()
            # 登记机关
            item['reg_address_name'] = self.merge_list(re.findall(r"class=[\"']tb[\"']>\s?登记机关\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip()
            # 所属行业
            item['industry'] = self.merge_list(re.findall(r"class=[\"']tb[\"']>\s?所属行业\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip()
            # 企业类型
            item['business_type'] = self.merge_list(re.findall(r"class=[\"']tb[\"']>\s?企业类型\s?</td>\s?<td.*?>(.*?)</td>", con, re.DOTALL)).strip()
            # 地址
            item['address'] = address.strip()
            # 省 市 区
            item['province'], item['city'], item['area'] = cpca.transform([item['address']]).loc[0, ['省', '市', '区']]
            return item
        except:
            return item

    @staticmethod
    def merge_list(in_list):
        """
        获取列表中的第一个元素
        @param in_list:
        @return: 提取后的数据
        """
        if len(in_list) >= 1:
            return in_list[0].strip()
        else:
            return ''

    def get_save_cookie(self):
        """
        判断是否存在cookie，不存在的话获取cookie
        @return:
        """
        # 判断是否存在保存cookie的文件，不存在则直接打开浏览器获取cookie
        if not os.path.exists(f'./save_cookie/{self.cookie_name}'):
            self.cookie = self.et_driver()
        else:
            # 如果存在cookie文件
            with open(f'./save_cookie/{self.cookie_name}', 'r', encoding='utf-8') as f:
                read_cookie = json.loads(f.read())
                ip_port = f'{socket.gethostbyname(socket.gethostname())}:{"0000"}'
                ip_port = read_cookie.get(ip_port, '')
                # 如果存在ip和port为键的键值对
                if ip_port:
                    now_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    time_c = parse(now_str) - parse(ip_port[0])
                    # 获取cookie的时间和当前时间差大于7天的时候重新获取cookie
                    if time_c.days >= 7:
                        self.cookie = self.et_driver()
                    else:
                        # 满足条件的话直接获取cookie
                        self.cookie = ip_port[1]
                else:
                    # 不存在ip和port的键值对的时候直接浏览器获取cookie
                    self.cookie = self.et_driver()

    def main(self):
        # 先获取cookie值
        self.get_save_cookie()
        # 获取url中的关键参数
        self.cbase = self.get_company_url()
        if self.cbase == '01':
            res = {}
            return res

        if not self.cbase:
            self.cookie = self.et_driver()
            self.cbase = self.get_company_url()
        # 获取电话邮箱
        tel_phone, email, address_o = self.get_tel_mail()
        # 基本工商信息和变更信息
        res = self.get_base_info(tel_phone, email, address_o)
        return res


if __name__ == '__main__':
    com = '浙江淘宝网络有限公司'
    print(QCC(com).main())
