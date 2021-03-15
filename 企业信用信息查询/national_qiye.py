import requests
import json
import re
import time


class NationalSystem(object):
    """
    通过国家企业信用信息公示系统app获取企业数据
    """
    def __init__(self, company_name):
        # cookie构成参数
        self.jsessionid = ''
        self.jsluid_h = ''
        self.sectoken = ''
        self.tlb_cookie = ''
        # 第二步获取到的下次请求的参数
        self.pripid_2 = ''
        self.nodenum_2 = ''
        self.enttype_2 = ''
        # 第三步获取到的下次请求的参数
        self.pripid_3 = ''
        self.nodenum_3 = ''
        self.enttype_3 = ''
        # 获取企业年报的参数
        self.ancheid = ''
        self.ancheyear = ''
        # 查找的公司
        self.company_name = company_name

    def sep_1(self):
        """
        第一步：获取cookie
        @return:
        """
        url = 'http://app.gsxt.gov.cn/gsxt/pubMsgList.html'
        headers = {
            'Host': 'app.gsxt.gov.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'file://',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; OPPO R11 Plus Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Html5Plus/1.0',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        data = {
            "sourceType":"A"
        }
        # 确保能够获取到正确的参数
        while True:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))
                get_cookie = response.headers.get('Set-Cookie')
                # 获取组成cookie的参数
                self.jsessionid = re.findall(r'JSESSIONID=(.*?);', get_cookie)[0]
                self.jsluid_h = re.findall(r'__jsluid_h=(.*?);', get_cookie)[0]
                self.sectoken = re.findall(r'SECTOKEN=(.*?);', get_cookie)[0]
                self.tlb_cookie = re.findall(r'tlb_cookie=(.*?);', get_cookie)[0]
                print(f'jsessionid: {self.jsessionid}, sectoken: {self.sectoken}, tlb_cookie: {self.tlb_cookie}, jsluid_h: {self.jsluid_h}')
                break
            except Exception as e:
                print(f'第一步获取cookie组成参数失败: {e}')
                time.sleep(2)

    def sep_2(self):
        """
        第二步：搜索企业(输入汉字会utf-8编码，获取不到数据)
        @return:
        """
        url = 'http://app.gsxt.gov.cn/gsxt/cn/gov/saic/web/controller/PrimaryInfoIndexAppController/search?page=1'
        headers = {
            'Cookie': f'JSESSIONID={self.jsessionid}; SECTOKEN={self.sectoken}; tlb_cookie={self.tlb_cookie}; __jsluid_h={self.jsluid_h}',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; OPPO R11 Plus Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Html5Plus/1.0',
            'Host': 'app.gsxt.gov.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        # 不要调整data的格式，否则会出错
        data = {"searchword":self.company_name,"conditions":{"excep_tab":"0","ill_tab":"0","area":"0","cStatus":"0","xzxk":"0","xzcf":"0","dydj":"0"},"sourceType":"A"}
        while True:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data)).json()
                # 下一步请求所需要的参数
                self.pripid_2 = response.get('data').get('result').get('data')[0].get('pripid')
                self.nodenum_2 = response.get('data').get('result').get('data')[0].get('nodeNum')
                self.enttype_2 = response.get('data').get('result').get('data')[0].get('entType')
                print(f'pripid_2: {self.pripid_2}, nodenum_2: {self.nodenum_2}, enttype_2: {self.enttype_2}')
                break
            except Exception as e:
                print(f'第二步获取第三步中的请求参数失败: {e}')
                time.sleep(2)

    def sep_3(self):
        """
        第三步：进入详情
        @return:
        """
        url = f'http://app.gsxt.gov.cn/gsxt/corp-query-entprise-info-primaryinfoapp-entbaseInfo-{self.pripid_2}.html?nodeNum={self.nodenum_2}&entType={self.enttype_2}&sourceType=A'
        data = {}
        headers = {
            'Host': 'app.gsxt.gov.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'file://',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; OPPO R11 Plus Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Html5Plus/1.0',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={self.jsessionid}; SECTOKEN={self.sectoken}; tlb_cookie={self.tlb_cookie}; __jsluid_h={self.jsluid_h}',
        }
        while True:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data)).json()
                self.pripid_3 = response.get('result').get('pripId')
                self.enttype_3 = response.get('result').get('entType')
                self.nodenum_3 = response.get('result').get('nodeNum')
                print(f'pripid_3: {self.pripid_3}, enttype_3: {self.enttype_3}, nodenum_3: {self.nodenum_3}')
                break
            except Exception as e:
                print(f'第三步获取下一步参数失败: {e}')
                time.sleep(2)

    def sep_4(self):
        """
        第四步: 获取企业年报所需参数
        @return:
        """
        url = f'http://app.gsxt.gov.cn/gsxt/corp-query-entprise-info-anCheYearInfo-{self.pripid_3}.html?nodeNum={self.nodenum_3}&entType={self.enttype_3}&sourceType=A'
        headers = {
            'Host': 'app.gsxt.gov.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'file://',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; OPPO R11 Plus Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Html5Plus/1.0',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={self.jsessionid}; SECTOKEN={self.sectoken}; tlb_cookie={self.tlb_cookie}; __jsluid_h={self.jsluid_h}',
        }
        data = {}
        while True:
            try:
                response = requests.post(url, headers=headers, data=data).json()
                self.ancheid = response[0].get('anCheId')
                self.ancheyear = response[0].get('anCheYear')
                print(f'ancheid: {self.ancheid}, ancheyear: {self.ancheyear}')
                break
            except Exception as e:
                print(f'第四步获取企业年报参数失败: {e}')
                time.sleep(2)

    def sep_5(self):
        """
        第五步: 获取企业年报数据
        @return:
        """
        url = f'http://app.gsxt.gov.cn/gsxt/corp-query-entprise-info-primaryinfoapp-annualReportInfo-{self.pripid_3}.html?nodeNum={self.nodenum_3}&anCheId={self.ancheid}&anCheYear={self.ancheyear}&entType={self.enttype_3}&sourceType=A'
        headers = {
            'Host': 'app.gsxt.gov.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'file://',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; OPPO R11 Plus Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Html5Plus/1.0',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={self.jsessionid}; SECTOKEN={self.sectoken}; tlb_cookie={self.tlb_cookie}; __jsluid_h={self.jsluid_h}',
        }
        data = {}
        while True:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))
                if response.status_code == 200:
                    break
            except Exception as e:
                print(f'第五步获取企业年报中的数据失败: {e}')
                time.sleep(2)

        try:
            response = response.json()
            item = dict()
            # 企业名称
            item['company_name'] = response.get('result').get('entName')
            # 法人
            item['contact'] = response.get('result').get('name')
            # 经营状态
            item['register_status'] = response.get('result').get('regState_CN')[:2]
            # 统一信用代码
            item['credit_code'] = response.get('result').get('uniscId')
            # 注册资本
            item['register_capital'] = response.get('result').get('regCap', 0) * 10000
            # 资本单位(人民币、美元等)
            item['register_currency'] = response.get('result').get('regCapCur_CN')
            # 地址
            item['address'] = response.get('result').get('dom')
            # 实缴资本
            all_peo_money = response.get('annRep').get('annRepDataSponsor')
            all_list_money = []
            for i in all_peo_money:
                all_list_money.append(i.get('liAcConAm', 0))
            mon = sum(all_list_money)
            if mon == 0:
                item['real_capital'] = item['register_capital']
            else:
                item['real_capital'] = sum(all_list_money) * 10000
            # 联系电话
            item['phone'] = response.get('annRep').get('annRepData').get('tel')
            # 邮箱
            item['mail'] = response.get('annRep').get('annRepData').get('email')
            # 人员规模
            item['staff_size'] = self.get_1_list(response.get('annRep').get('annRepDataSocsecinfo')).get('so110', 0)
            # 官网
            item['official_url'] = self.get_1_list(response.get('annRep').get('annRepDataWebsite')).get('domain', '')
            print(item)
        except Exception as e:
            print(f'第五步获取企业年报中的数据失败: {e}')
            time.sleep(2)

    @staticmethod
    def get_1_list(in_list):
        if len(in_list) >= 1:
            return in_list[0]
        else:
            return {}

    def main(self):
        # 第一步 获取cookie组成参数
        self.sep_1()
        # 第二步搜索
        self.sep_2()
        # 第三步进入详情
        self.sep_3()
        # 第四步获取企业年报参数
        self.sep_4()
        # 第五步获取企业年报中的数据
        self.sep_5()


if __name__ == '__main__':
    com_code = '913301107517434382'
    # com_code = '浙江淘宝网络有限公司'
    NationalSystem(com_code).main()
