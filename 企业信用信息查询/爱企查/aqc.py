import requests
import time
import re
import cpca

from requests.adapters import HTTPAdapter
from fake_useragent import UserAgent
from requests.packages import urllib3
from urllib.parse import quote


urllib3.disable_warnings()

requests.adapters.DEFAULT_RETRIES = 3
s = requests.Session()
s.keep_alive = False


class AiQiCha(object):
    def __init__(self, keyword):
        self.get_pid_url = 'https://aiqicha.baidu.com/s/l?q={}&t=&p=1&s=100&o=&f=%7B%7D'
        self.info_url = 'https://aiqicha.baidu.com/detail/basicAllDataAjax?pid={}'
        # 通过企业年报获取实缴资本
        self.q_year_p = 'https://aiqicha.baidu.com/annualreport?pid={}&year={}'
        # 搜索关键词
        self.search_key = keyword

    def get_pid(self):
        """
        获取企业的pid
        @return:
        """
        # 将汉字编码
        q = quote(self.search_key)
        headers = {
            'Host': 'aiqicha.baidu.com',
            'Referer': f'https://aiqicha.baidu.com/s?q={q}&t=0',
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        for i in range(3):
            try:
                response = s.get(self.get_pid_url.format(self.search_key), headers=headers, verify=False)
                page_data = response.json().get('data').get('resultList')[0].get('pid')
                # 如果获取到pid
                if page_data:
                    res_info = self.get_info(page_data)
                    return res_info
                else:
                    time.sleep(3)
            except:
                pass

    def get_info(self, pid):
        """
        获取企业的相关信息
        @param pid: 企业的编号
        @return:
        """
        headers = {
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        try:
            res = s.get(self.info_url.format(pid), headers=headers, verify=False, timeout=10)
            json_data = res.json()
        except:
            return {}
        else:
            # 获取工商信息
            return self.company_info(json_data)

    @staticmethod
    def money(mo):
        """
        分离资金中的钱和单位
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
    def join_list(in_list):
        """
        获取列表的第一个元素
        @param in_list: 列表
        @return:
        """
        try:
            return in_list[0]
        except:
            return ''

    @staticmethod
    def deal_par(in_par):
        """
        把None等转换成 ''
        @param in_par:
        @return:
        """
        return '' if not in_par else in_par

    def company_info(self, in_data):
        """
        获取企业工商信息
        @return: 获取到的工商信息
        """
        item_info = {}
        try:
            # 获取工商数据
            basic_data = in_data['data']['basicData']
            # 公司名
            item_info['company_name'] = basic_data.get('entName', '')
            # 法定代表人
            item_info['legal'] = self.deal_par(basic_data.get('legalPerson', '')).replace('-', '')
            # 电话
            item_info['phone'] = self.deal_par(basic_data.get('telephone', '')).replace('-', '')
            # 邮箱
            item_info['email'] = self.deal_par(basic_data.get('email', '')).replace('-', '')
            # 状态
            item_info['register_status'] = self.deal_par(basic_data.get('openStatus', ''))
            # 企业官网
            item_info['official_url'] = self.deal_par(basic_data.get('website', '')).replace('-', '')
            # 注册资本
            item_info['register_capital'], item_info['register_currency'] = self.money(self.deal_par(basic_data.get('regCapital', '')))
            # 实缴资本
            item_info['real_capital'], item_info['real_currency'] = self.money(self.deal_par(basic_data.get('realCapital', '')))
            # 统一社会信用代码
            item_info['credit_code'] = self.deal_par(basic_data.get('regNo', '')).replace('-', '')
            # 工商注册号
            item_info['business_number'] = self.deal_par(basic_data.get('licenseNumber', '')).replace('-', '')
            # 登记机关
            item_info['reg_address_name'] = self.deal_par(basic_data.get('authority', '')).replace('-', '')
            # 所属行业
            item_info['industry'] = self.deal_par(basic_data.get('industry', '')).replace('-', '')
            # 企业类型
            item_info['business_type'] = self.deal_par(basic_data.get('entType', '')).replace('-', '')
            # 行政区划
            item_info['district'] = basic_data.get('district', '').strip()
            # 地址
            item_info['address'] = self.deal_par(basic_data.get('regAddr', '')).strip()
            # 省 市 区
            item_info['province'], item_info['city'], item_info['area'] = cpca.transform([f"{item_info['district']}{item_info['address']}"]).loc[0, ['省', '市', '区']]
            return item_info
        except:
            return {}

    def main(self):
        return self.get_pid()


if __name__ == '__main__':
    print(AiQiCha('浙江淘宝网络有限公司').main())
