import requests
import time
import random
import json
import os

from fake_useragent import UserAgent
from lxml import etree


class TianYan(object):
    def __init__(self):
        self.url_category = 'https://www.tianyancha.com/'
        self.useragent = UserAgent()

    def get_category(self):
        """获取查询输入信息并保存到json中"""
        req = requests.get(self.url_category, headers={'User-Agent': self.useragent.random}).text
        html_req = etree.HTML(req)
        # 地域名和url
        prov_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][1]/div[@class="row"]/div/a/text()')
        prov_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][1]/div[@class="row"]/div/a/@href')
        # 行业名和url
        industry_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][2]/div[@class="row"]/div/a/text()')
        industry_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][2]/div[@class="row"]/div/a/@href')
        # 最新注册企业
        register_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][3]/div[@class="col-4"]/div[@class="company-card"]/div/a/text()')
        register_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][3]/div[@class="col-4"]/div[@class="company-card"]/div/a/@href')
        # 热门律所
        law_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][4]/div[@class="col-3"]/div[@class="hot"]/a/text()')
        law_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][4]/div[@class="col-3"]/div[@class="hot"]/a/@href')
        # 热门人物
        human_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][5]/div[@class="col-3"]/div[@class="hot"]/a/text()')
        human_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][5]/div[@class="col-3"]/div[@class="hot"]/a/@href')
        # 最新上市企业
        ipo_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][6]/div[@class="col-4"]/div[@class="company-card"]/div[@class="box"]/a/text()')
        ipo_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][6]/div[@class="col-4"]/div[@class="company-card"]/div[@class="box"]/a/@href')
        # 最新融资企业
        finance_names = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][7]/div[@class="col-4"]/div[@class="company-card"]/div[@class="box"]/a/text()')
        finance_urls = html_req.xpath('//div[@class="container content"]/div[contains(@class,"js-industry-container")][7]/div[@class="col-4"]/div[@class="company-card"]/div[@class="box"]/a/@href')

        prov = zip(prov_names, prov_urls)
        industry = zip(industry_names, industry_urls)
        register = zip(register_names, register_urls)
        law = zip(law_names, law_urls)
        human = zip(human_names, human_urls)
        ipo = zip(ipo_names, ipo_urls)
        finance = zip(finance_names, finance_urls)

        contents = [prov, industry, register, law, human, ipo, finance]
        prov_dict = {}
        industry_dict = {}
        register_dict = {}
        law_dict = {}
        human_dict = {}
        ipo_dict = {}
        finance_dict = {}
        contents_dict = {
            prov: prov_dict,
            industry: industry_dict,
            register: register_dict,
            law: law_dict,
            human: human_dict,
            ipo: ipo_dict,
            finance: finance_dict
        }
        item_dict = {
            prov: '地域',
            industry: '行业',
            register: '最新注册企业',
            law: '热门律所',
            human: '热门人物',
            ipo: '最新上市企业',
            finance: '最新融资企业'
        }
        # 保存最后的数据，{'地域':{'北京':'url', '天津':'url'}, {'行业':{'林业':'url', '渔业': 'url'}}}
        item = {}
        for content in contents:
            for name, url in content:
                contents_dict[content][name] = url

            item[item_dict[content]] = contents_dict[content]

        print(item)
        with open('query_info.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False))

    def manage_url(self, company_type, base_url):
        if company_type == '地域':
            url_split = base_url.split('?')
            url = url_split[0] + '/p{}?' + url_split[1]
            self.get_company_url(url)
        elif company_type == '行业':
            url = base_url + '/p{}'
            self.get_company_url(url)
        elif company_type in ['最新注册企业', '热门律所', '最新上市企业', '最新融资企业']:
            self.get_company_detail(base_url)
        elif company_type == '热门人物':
            self.get_people(base_url)

    def get_company_url(self, url):
        """获取公司信息的详细链接"""
        for i in range(1, 6):
            print(url.format(i))
            company_req = requests.get(url.format(i), headers={'User-Agent': self.useragent.random}).text
            company_html = etree.HTML(company_req)
            # 获取一页中所有进入公司详细页面的url
            company_urls = company_html.xpath('//div[contains(@class,"result-list")]/div[contains(@class,"search-item")]/div[contains(@class,"search-result-single")]/div[@class="content"]/div[@class="header"]/a/@href')

            for company_url in company_urls:
                self.get_company_detail(company_url)
                time.sleep(random.uniform(1, 3))

            time.sleep(random.uniform(2, 4))

    def get_company_detail(self, company_url):
        """获取每个公司的具体的信息"""
        detail_req = requests.get(company_url, headers={'User-Agent': self.useragent.random}).text
        detail_html = etree.HTML(detail_req)
        item = dict()
        # 公司名称
        item['name'] = self.join_list(detail_html.xpath('//div[@class="content"]/div[@class="header"]/h1/text()'))
        # 公司网址
        item['company_link'] = self.join_list(detail_html.xpath('//div[@class="content"]/div[@class="detail"]//a[@class="company-link"]/text()'))
        # 法定代表人
        item['company_human'] = self.join_list(detail_html.xpath('//table[@class="table"]//div[@class="humancompany"]//a/text()'))
        # 注册资本
        item['money'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]/tbody/tr[1]/td[2]/div/text()'))
        # 实缴资本
        item['ready_money'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[1]/td[4]/text()'))
        # 评分
        item['score'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[1]/td[5]/div[@class="sort-score"]/span[@class="sort-score-value"]/text()'))
        # 成立日期
        item['estab_date'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[2]/td[2]/div/text()'))
        # 经营状态
        item['status'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[2]/td[4]/text()'))
        # 统一社会信用代码
        item['credit_code'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[3]/td[2]/text()'))
        # 工商注册号
        item['registration_number'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[3]/td[4]/text()'))
        # 纳税人识别号
        item['taxpayer_code'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[4]/td[2]/text()'))
        # 组织机构代码
        item['organization_code'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[4]/td[4]/text()'))
        # 公司类型
        item['company_type'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[5]/td[2]/text()'))
        # 行业
        item['industry'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[5]/td[4]/text()'))
        # 核准日期
        item['issue_date'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[6]/td[2]/text/text()'))
        # 登记机关
        item['registrar'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[6]/td[4]/text()'))
        # 营业期限
        item['business_term'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[7]/td[2]/span/text()'))
        # 纳税人资质
        item['taxpayer_qualification'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[7]/td[4]/text()'))
        # 人员规模
        item['staff_size'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[8]/td[2]/text()'))
        # 参保人数
        item['insured_persons'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[8]/td[4]/text()'))
        # 曾用名
        item['old_name'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[9]/td[2]/text()'))
        # 英文名称
        item['english_name'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[9]/td[4]/text()'))
        # 注册地址
        item['registered_address'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[10]/td[2]/text()'))
        # 经营范围
        item['business_scope'] = self.join_list(detail_html.xpath('//div[@id="_container_baseInfo"]/table[contains(@class,"table")]//tr[11]/td[2]/span/text()'))

        print(item)
        self.save_json(item)

    def get_people(self, url):
        """热门人物信息获取"""
        print(url)
        people_req = requests.get(url, headers={'User-Agent': self.useragent.random}).text
        people_html = etree.HTML(people_req)
        item = dict()
        # 人物姓名
        item['people_name'] = self.join_list(people_html.xpath('//div[@class="result-human-list"]//div[@class="content"]/a/text()'))
        # 公司
        item['people_company'] = self.join_list(people_html.xpath('//div[@class="result-human-list"]//div[@class="bottom"]/div[@class="total"]/div[@class="company"]/a/text()'))
        # 公司地址
        item['people_addr'] = self.split_str(self.join_list(people_html.xpath('//div[@class="result-human-list"]//div[@class="bottom"]/div[@class="total"]/div[@class="province"]/text()[1]')))
        print(item)
        self.save_json(item)

    @staticmethod
    def join_list(con):
        """拼接列表中的每个元素"""
        res = ''.join(con)
        if not res:
            return '暂无消息'
        return ''.join(con)

    @staticmethod
    def split_str(con):
        try:
            res = con.split('（')
        except:
            res = con.split('(')

        if res:
            return res[0]
        else:
            return ''

    @staticmethod
    def save_json(item):
        with open('save_json.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def main(self):
        while True:
            # 在当前路径下查看是否存在query_info.json文件，返回True或者False
            flag = os.path.exists('query_info.json')
            if flag:
                # 打开读取文件内容
                with open('query_info.json', 'r', encoding='utf-8') as f:
                    con = json.loads(f.read())

                query_way = input('请输入查询方式(地域、行业、最新注册企业、热门律所、热门人物、最新上市企业、最新融资企业)：')

                flag_i = False
                for i in ['地域', '行业', '最新注册企业', '热门律所', '热门人物', '最新上市企业', '最新融资企业']:
                    # 如果输入的信息在给定的列表中
                    if query_way == i or query_way in i:
                        flag_i = True
                        info = input('请输入具体信息(北京、河北、西安、医药制造业等)：').strip()
                        flag_info = False
                        # 比较字典和输入的信息
                        for key, value in con[i].items():
                            if info in key:
                                try:
                                    url = con[i][key]
                                except:
                                    pass
                                else:
                                    flag_info = True
                                    self.manage_url(i, url)
                        if not flag_info:
                            print('未查找到该信息，请检查具体信息输入是否正确！')
                if not flag_i:
                    print('请检查地域、行业等信息受否输入正确！')
                # 如果信息正确则推出while
                break
            else:
                print('文件不存在！重新获取中，请稍后重新查询！')
                self.get_category()


if __name__ == '__main__':
    ty = TianYan()
    ty.main()

