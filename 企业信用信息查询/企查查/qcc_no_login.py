import requests
import time
import re
import os
import socket
import json
import cpca

from fake_useragent import UserAgent
from requests.packages import urllib3
from selenium import webdriver
from dateutil.parser import parse
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait


urllib3.disable_warnings()


class QCC(object):
    def __init__(self, company_name):
        """
        @param company_name: 需要查找的公司名
        """
        self.qcc_url = 'https://www.qcc.com/'
        # 搜索名称url
        self.search_url = '''https://www.qcc.com/web/search?key={}'''
        # 公司域名
        self.domain_url = 'https://www.qcc.com/cbase/{}'
        # 保存cookie的文件名
        self.cookie_name = f'qcc_cookie_no_login.json'
        # 公司名称
        self.company_name = company_name
        # 保存cookie
        self.cookie = ''

    def get_company_url(self):
        """
        获取进入公司详情的url
        @return: 请求到的数据
        """
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random,
            'Cookie': self.cookie,
            'Referer': 'https://www.qcc.com/',
        }
        url = self.search_url.format(f'{self.company_name}')
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
        except Exception as e:
            print(f'获取{url}出错，{e}')
            return {}
        else:
            page_source = response.text.replace(' ', '').replace('\n', '')
            # 没有的对应的公司
            if '小查没有找到相关数据' in page_source or '建议更换一下搜索词' in page_source:
                return {}

            if '过于频繁' in page_source or 'arg1' in page_source:
                self.cookie = self.yanzheng()
                time.sleep(60 * 3)
                self.main()

            # 能查到数据
            if self.company_name in page_source:
                # 获取公司请求的参数
                base_par = self.merge_list(re.findall(r'[\'"]KeyNo[\'"][:：]\s?[\'"](.*?)[\'"],', page_source))
                # 公司请求的url
                company_url = self.domain_url.format(base_par)
                item = dict()
                # 法人
                item['legal'] = self.merge_list(re.findall(r'[\'"]OperName[\'"][:：]\s?[\'"](.*?)[\'"],', page_source))
                # 状态
                item['register_status'] = self.merge_list(re.findall(r'[\'"]ShortStatus[\'"][:：]\s?[\'"](.*?)[\'"]}', page_source))
                # 电话
                item['phone'] = self.merge_list(re.findall(r'[\'"]ContactNumber[\'"][:：]\s?[\'"](.*?)[\'"],', page_source))
                # 邮箱
                item['email'] = self.merge_list(re.findall(r'[\'"]Email[\'"][:：]\s?[\'"](.*?)[\'"],', page_source))
                # 官网
                item['official_url'] = self.merge_list(re.findall(r'[\'"]GW[\'"][:：]\s?[\'"](.*?)[\'"],', page_source)).replace(r'\u002F', '/')
                # 地址
                item['address'] = self.merge_list(re.findall(r'[\'"]Address[\'"][:：]\s?[\'"](.*?)[\'"],', page_source)).replace(r'\u003Cem\u003E', '').replace(r'\u003C\u002Fem\u003E', '')
                # 获取详情信息(工商信息和变更信息)
                info = self.get_company_info(company_url, item)
                return info
            else:
                time.sleep(2)

    def get_company_info(self, company_url, item):
        """
        获取工商信息和变更信息
        @param item:
        @param company_url: 公司请求url
        @return: 返回获取到的数据
        """
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random,
            'cookie': self.cookie,
        }
        try:
            response_com = requests.get(company_url, headers=headers, verify=False)
            company_response = response_com.text.replace(' ', '').replace('\n', '')
        except Exception as e:
            print(f'获取失败! {self.company_name} --> {company_url}--> {e}')
            return {}
        else:
            time.sleep(1)
            # 公司名
            item['company_name'] = self.merge_list(re.findall(r'<h1>(.*?)</h1>', company_response))
            # 注册资本
            register_capital = ''.join(re.findall(r'<tdclass=["\']tb["\']>注册资本</td><td.*?>(.*?)</td>', company_response, re.DOTALL))
            item['register_capital'], item['register_currency'] = self.money(re.sub(r'[\n 注册资本：:]', '', register_capital, re.DOTALL))
            # 实缴资本
            register_capital = ''.join(re.findall(r'<tdclass=["\']tb["\']>实缴资本</td><td.*?>(.*?)<', company_response, re.DOTALL))
            item['real_capital'], item['real_currency'] = self.money(re.sub(r'[\n 实缴资本：:]', '', register_capital, re.DOTALL))
            # 统一社会信用代码
            credit_code = ''.join(re.findall(r'<tdclass=["\']tb["\']>统一社会信用代码</td><tdclass=["\']["\']>(.*?)</td>', company_response, re.DOTALL))
            item['credit_code'] = re.sub(r'[\n 统一社会信用代码：:-]', '', credit_code, re.DOTALL)
            # 工商注册号
            business_number = ''.join(re.findall(r'<tdclass=["\']tb["\']>工商注册号</td><tdclass=["\']["\']>(.*?)</td>', company_response, re.DOTALL))
            item['business_number'] = re.sub(r'[\n 工商注册号：:-]', '', business_number, re.DOTALL)
            # 登记机关
            reg_addr = ''.join(re.findall(r'<tdwidth=["\'][0-9]{0,}%["\']class=["\']tb["\']>登记机关</td><tdwidth=["\'][0-9]{0,}%["\']class=["\']["\']>(.*?)</td>', company_response, re.DOTALL))
            item['reg_address_name'] = re.sub(r'[\n 登记机关：:-]', '', reg_addr, re.DOTALL)
            # 所属行业
            industry = ''.join(re.findall(r'<tdclass=["\']tb["\']>所属行业</td><tdclass=["\']["\']>(.*?)</td>', company_response, re.DOTALL)).strip()
            item['industry'] = re.sub(r'[\n 所属行业：:-]', '', industry, re.DOTALL)
            # 企业类型
            business_type = ''.join(re.findall(r'<tdwidth=["\'][0-9]{0,}%["\']class=["\']tb["\']>企业类型</td><tdwidth=["\'][0-9]{0,}%["\']class=["\']["\']>(.*?)</td>', company_response, re.DOTALL)).strip()
            item['business_type'] = re.sub(r'[\n 企业类型：:-]', '', business_type, re.DOTALL)
            # 省 市 区
            item['province'], item['city'], item['area'] = cpca.transform([item['address']]).loc[0, ['省', '市', '区']]
            return item

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

    def et_driver(self):
        """
        创建浏览器获取cookie
        @return:
        """
        print('正在创建模拟浏览器，请稍后！')
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
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
        try:
            driver.quit()
        except:
            pass
        return cookie

    def yanzheng(self):
        """
        创建浏览器获取cookie
        @return:
        """
        print('正在创建模拟浏览器，请稍后！')
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
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
        while True:
            u = 'https://www.qcc.com/index_verify?type=companysearch&back=%2Fweb%2Fsearch%3Fkey%3Dtaobao'
            driver.get(u)
            time.sleep(1)
            # 拖动滑块
            action = ActionChains(driver)
            # 滑块的id
            start = WebDriverWait(driver, 20, 0.2).until(lambda x: x.find_element_by_xpath('//div[@id="dom_id"]//div[contains(@id,"n1t")]/span[contains(@id, "n1z")]'))
            # 长按
            action.click_and_hold(start)
            # 滑动滑块
            action.drag_and_drop_by_offset(start, 308, 0).perform()
            time.sleep(3)
            driver.find_element_by_xpath('//*[@id="verify"]').click()
            time.sleep(5)
            if driver.current_url != u:
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
                try:
                    driver.quit()
                except:
                    pass
                return cookie
            else:
                time.sleep(1)

    def main(self):
        """
        判断本地是否保存有登录后的cookie值，没有则进行登录保存
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
                    if time_c.seconds >= 300:
                        self.cookie = self.et_driver()
                    else:
                        # 满足条件的话直接获取cookie
                        self.cookie = ip_port[1]
                else:
                    # 不存在ip和port的键值对的时候直接浏览器获取cookie
                    self.cookie = self.et_driver()

        return self.get_company_url()


if __name__ == '__main__':
    com = '浙江淘宝网络有限公司'
    print(QCC(com).main())
