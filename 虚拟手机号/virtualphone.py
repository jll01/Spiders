import requests
import urllib3
import random
import re
import time
import pymysql
import json
import requests.adapters

from lxml import etree


class VirtualPhone(object):

    def __init__(self):
        self.page = 1
        self.url = 'https://www.pdflibr.com/?page={}'
        self.content_page = 1
        # self.content_url = 'https://www.pdflibr.com/SMSContent/1?page={}'
        headers = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
        ]
        self.headers = {
            # 'referer': 'https://www.pdflibr.com/SMSContent/1',
            'user-agent': random.choice(headers),
        }

        ip = [
            '117.191.11.113:80',
            '117.191.11.109:8080',
            '117.191.11.80:80',
            '117.191.11.76:8080',
            '117.191.11.80:80',
            '117.191.11.111:80',
            '117.191.11.109:8080',
            '39.135.24.11:80',
            '117.191.11.108:8080',
            '117.191.11.110:8080',
            '39.137.69.7:80',
            '39.137.69.10:8080',
        ]
        self.proxies = {
            'http': random.choice(ip),
        }

        # self.session = requests.session()
        # 数据库
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', passwd='0000', db='scrapytest')
        self.cur = self.connect.cursor()

    def join_list(self,res):

        if len(res) != 0:
            return res[0].strip()
        else:
            return ''

    def get_fromcontent(self,res):
        try:
            return re.findall(r'【(.*?)】',res)[0]
        except Exception as e:
            try:
                return re.findall(r'\[(.*?)\]',res)[0]
            except Exception as e:
                return '未知来源'

    def get_url(self):
        urllist = []
        saveurls = []
        while self.page <= 10:
            page = requests.get(self.url.format(self.page), headers=self.headers, proxies=self.proxies, verify=False).text
            html = etree.HTML(page)
            urls = html.xpath('//div[@class="container-fluid"]/div[contains(@class,"sms-number-list")]/div[contains(@class,"sms-number-read")]/a/@href')
            phones = html.xpath('//div[@class="container-fluid"]/div[contains(@class,"sms-number-list")]/div[contains(@class,"number-list-flag")]/h3/text()')
            contents = zip(urls,phones)
            for content in contents:
                item = {}
                if content[0] not in saveurls:
                    item['url'] = 'https://www.pdflibr.com' + content[0]
                    item['phone'] = content[1]
                    urllist.append(item)
                    saveurls.append(content[0])

            self.page += 1
            time.sleep(random.randint(2,4))

        with open('phoneurl.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(urllist, ensure_ascii=False))

        return urllist

    def requests_url(self):
        print('正在获取每个虚拟手机号的详情链接！请耐心等待！')
        with open('phoneurl.json', 'r', encoding='utf-8') as f:
            urllist = f.read()
        if len(urllist) == 0:
            urllist = self.get_url()
        else:
            urllist = json.loads(urllist)
            print(urllist)

        for request in urllist:
            self.get_content(request['phone'],request['url'])
            # time.sleep(random.randint(3,5))

    def get_content(self,phone,url):
        while True:
            try:
                response = requests.get(url + '?page={}'.format(self.content_page), headers=self.headers, proxies=self.proxies, verify=False).text
            except Exception as e:
                print('请求{}时出错{}'.format(url + '?page={}'.format(self.content_page),e))
            else:
                html = etree.HTML(response)

                contents = html.xpath('//section[@class="container-fluid sms_content"]/div[@class="container sms-content-list"]/div[@class="sms-content-table table-responsive"]/table[@class="table table-hover"]/tbody/tr')
                if len(contents) != 0:
                    for content in contents:
                        item = {}
                        item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                        item['virtualphone'] = phone
                        item['fromphone'] = self.join_list(content.xpath('./td[2]/text()'))
                        con = self.join_list(content.xpath('./td[3]/text()'))
                        item['origin'] = self.get_fromcontent(con)
                        item['content'] = con
                        item['getdate'] = self.join_list(content.xpath('./td[4]/time/text()'))

                        print(item)
                        self.save_data(item)
                    print('----------{}下载完成！----------'.format(url + '?page={}'.format(self.content_page)))

                    time.sleep(random.randint(1,2))

                    self.content_page += 1
                else:
                    break

    def save_data(self,item):
        '''保存数据'''
        self.cur.execute(
            """insert into virtualphone (spidertime,virtualphone,fromphone,origin,getdate,content) values (%s,%s,%s,%s,%s,%s)""",
            (
                item['spidertime'],
                item['virtualphone'],
                item['fromphone'],
                item['origin'],
                item['getdate'],
                item['content'],
            ))
        self.connect.commit()

    def main(self):
        # self.get_content()
        self.requests_url()

if __name__ == '__main__':
    urllib3.disable_warnings()
    requests.adapters.DEFAULT_RETRIES = 5

    s = requests.session()
    s.keep_alive = False

    vp = VirtualPhone()
    vp.main()