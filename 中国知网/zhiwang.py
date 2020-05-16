#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   zhiwang.py
# @Time    :   2019/7/15 20:46
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import time
import re
import pymysql

from lxml import etree
from urllib import parse


class Zhiwang(object):
    def __init__(self,key_word):
        self.session = requests.session()
        self.key_word = key_word
        self.page = 1
        self.conn=pymysql.connect(host='localhost',port=3306,db='scrapytest',user='root',passwd='0000')
        self.cur = self.conn.cursor()

    def get_in(self):
        '''知网入口'''
        url_in = 'http://kns.cnki.net/kns/brief/default_result.aspx'
        data_in = {
            'txt_1_sel': 'SU$%=|',
            'txt_1_value1': self.key_word,
            'txt_1_special1': '%',
            'txt_extension': '',
            'expertvalue': '',
            'cjfdcode': '',
            'currentid': 'txt_1_value1',
            'dbJson': 'coreJson',
            'dbPrefix': 'SCDB',
            'db_opt': 'CJFQ,CJRF,CDFD,CMFD,CPFD,IPFD,CCND,CCJD',
            'db_value': '',
            'hidTabChange': '',
            'hidDivIDS': '',
            'singleDB': 'SCDB',
            'db_codes': '',
            'singleDBName': '',
            'againConfigJson': 'false',
            'action': 'scdbsearch',
            'ua': '1.11',
        }
        headers_in = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Ecp_ClientId=8190715194701775788; Ecp_IpLoginFail=190715118.183.95.80; UM_distinctid=16bf57718384fb-06b1ace813c13e-f353163-144000-16bf57718396bc; RsPerPage=20; cnkiUserKey=17695ce0-f65c-a154-da81-67cd926f5bc3; ASP.NET_SessionId=zj0u3rtaurb12skgtztm43pw; SID_kns=123116; SID_klogin=125143; KNS_SortType=; SID_crrs=125131; _pk_ref=%5B%22%22%2C%22%22%2C1563240337%2C%22http%3A%2F%2Fwww.cnki.net%2Fold%2F%22%5D; _pk_ses=*; SID_krsnew=125134; SID_kcms=124112',
            'Host': 'kns.cnki.net',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
        }
        response_in = self.session.post(url_in, data=data_in, headers=headers_in)

    def get_list(self):
        '''获取文章列表页'''
        while True:
            url_list = 'http://kns.cnki.net/kns/brief/brief.aspx?'
            date = int(time.time()*1000)
            if self.page == 1:
                data_list = {
                    'pagename': 'ASP.brief_default_result_aspx',
                    'isinEn': '1',
                    'dbPrefix': 'SCDB',
                    'dbCatalog': '中国学术文献网络出版总库',
                    'ConfigFile': 'SCDBINDEX.xml',
                    'research': 'off',
                    't': date,
                    'keyValue': 'python',
                    'S': '1',
                    'sorttype': '',
                }
                headers_list = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Cookie': 'Ecp_ClientId=8190715194701775788; UM_distinctid=16bf57718384fb-06b1ace813c13e-f353163-144000-16bf57718396bc; RsPerPage=20; cnkiUserKey=17695ce0-f65c-a154-da81-67cd926f5bc3; Ecp_IpLoginFail=190716118.182.176.49; ASP.NET_SessionId=5rcy33i00myuyikhzcgppqze; SID_kns=123123; SID_klogin=125144; KNS_SortType=; SID_crrs=125133; _pk_ref=%5B%22%22%2C%22%22%2C1563282905%2C%22http%3A%2F%2Fwww.cnki.net%2Fold%2F%22%5D; _pk_ses=*; SID_krsnew=125132',
                    'Host': 'kns.cnki.net',
                    'Pragma': 'no-cache',
                    'Referer': 'http://kns.cnki.net/kns/brief/default_result.aspx',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                }
            elif self.page == 2:
                data_list = {
                    'curpage': self.page,
                    'RecordsPerPage': '20',
                    'QueryID': '4',
                    'ID': '',
                    'turnpage': '1',
                    'tpagemode': 'L',
                    'dbPrefix': 'SCDB',
                    'Fields': '',
                    'DisplayMode': 'listmode',
                    'PageName': 'ASP.brief_default_result_aspx',
                    'isinEn': '1',
                }
                headers_list = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Cookie': 'Ecp_ClientId=8190715194701775788; UM_distinctid=16bf57718384fb-06b1ace813c13e-f353163-144000-16bf57718396bc; RsPerPage=20; cnkiUserKey=17695ce0-f65c-a154-da81-67cd926f5bc3; Ecp_IpLoginFail=190716118.182.176.49; ASP.NET_SessionId=5rcy33i00myuyikhzcgppqze; SID_kns=123123; SID_klogin=125144; KNS_SortType=; SID_crrs=125133; _pk_ref=%5B%22%22%2C%22%22%2C1563282905%2C%22http%3A%2F%2Fwww.cnki.net%2Fold%2F%22%5D; _pk_ses=*; SID_krsnew=125132',
                    'Host': 'kns.cnki.net',
                    'Pragma': 'no-cache',
                    'Referer': 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t={}&keyValue=python&S=1&sorttype='.format(date),
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                }
            else:
                data_list = {
                    'curpage': self.page,
                    'RecordsPerPage': '20',
                    'QueryID': '4',
                    'ID': '',
                    'turnpage': '1',
                    'tpagemode': 'L',
                    'dbPrefix': 'SCDB',
                    'Fields': '',
                    'DisplayMode': 'listmode',
                    'PageName': 'ASP.brief_default_result_aspx',
                    'isinEn': '1',
                }
                headers_list = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Cookie': 'Ecp_ClientId=8190715194701775788; UM_distinctid=16bf57718384fb-06b1ace813c13e-f353163-144000-16bf57718396bc; RsPerPage=20; cnkiUserKey=17695ce0-f65c-a154-da81-67cd926f5bc3; Ecp_IpLoginFail=190716118.182.176.49; ASP.NET_SessionId=5rcy33i00myuyikhzcgppqze; SID_kns=123123; SID_klogin=125144; KNS_SortType=; SID_crrs=125133; _pk_ref=%5B%22%22%2C%22%22%2C1563282905%2C%22http%3A%2F%2Fwww.cnki.net%2Fold%2F%22%5D; _pk_ses=*; SID_krsnew=125132',
                    'Host': 'kns.cnki.net',
                    'Pragma': 'no-cache',
                    'Referer': 'http://kns.cnki.net/kns/brief/brief.aspx?curpage={}&RecordsPerPage=20&QueryID=11&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_default_result_aspx&isinEn=1&'.format(self.page-1),
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                }

            res = self.session.get(url_list+parse.urlencode(data_list),headers=headers_list).content
            response_list = etree.HTML(res)
            try:
                connects = response_list.xpath('//tr[@bgcolor="#f6f7fb"]|//tr[@bgcolor="#ffffff"]')
            except Exception as e:
                print('到末尾了！e'.format(e))
                break
            else:
                self.page += 1
                self.get_detail(connects)

            time.sleep(3)

    def get_detail(self,connects):
        detail_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Ecp_ClientId=8190715194701775788; Ecp_IpLoginFail=190715118.183.95.80; UM_distinctid=16bf57718384fb-06b1ace813c13e-f353163-144000-16bf57718396bc; RsPerPage=20; cnkiUserKey=17695ce0-f65c-a154-da81-67cd926f5bc3; ASP.NET_SessionId=zj0u3rtaurb12skgtztm43pw; SID_kns=123116; SID_klogin=125143; KNS_SortType=; SID_crrs=125131; _pk_ref=%5B%22%22%2C%22%22%2C1563240337%2C%22http%3A%2F%2Fwww.cnki.net%2Fold%2F%22%5D; _pk_ses=*; SID_krsnew=125134; SID_kcms=124112',
            'Host': 'kns.cnki.net',
            'Pragma': 'no-cache',
            'Referer': 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t={}&keyValue=python&S=1&sorttype='.format(int(time.time()*1000)),
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
        }

        for connect in connects:
            paper_link = connect.xpath("td/a[@class='fz14']/@href")[0]
            fileName = re.findall(r'FileName=(.*?)&', paper_link)[0]
            dbName = re.findall(r'DbName=(.*?)&', paper_link)[0]
            dbCode = re.findall(r'DbCode=(.*?)&', paper_link)[0]
            data = {
                'dbcode': dbCode,
                'dbname': dbName,
                'filename': fileName
            }
            url_detail = 'http://kns.cnki.net/KCMS/detail/detail.aspx?' + parse.urlencode(data)
            detail = self.session.get(url_detail,headers=detail_headers).text
            detail_con = etree.HTML(detail)
            self.get_connect(detail_con,url_detail)



    def get_connect(self,detail_con,url_detail):
        item = {}

        try:
            item['title'] = detail_con.xpath('//div[@class="wxmain"]/div[@class="wxTitle"]/h2/text() | //*[@id="entitle"]/text()')[0]
        except Exception as e:
            print('一条数据出错了！{}'.format(e))
        else:
            authors = detail_con.xpath('//div[@class="wxmain"]/div[@class="wxTitle"]/div[@class="author"]/span | //div[@class="wxmain"]/div[@class="wxTitle"]/div[@class="authorE"]/span')
            authors_1 = detail_con.xpath('/html/body/div[1]/div[2]/div[1]/table/tbody/tr[1]/td[2]/a')
            if len(authors) != 0:
                name = []
                for author in authors:
                    name.append(author.xpath('./a/text() | ./text()')[0])
                item['author'] = '|'.join(name)
            elif len(authors_1) != 0:
                name = []
                for author in authors:
                    name.append(author.xpath('./text()')[0])
                item['author'] = '|'.join(name)
            else:
                item['author'] = ''

            units = detail_con.xpath('//div[@class="wxmain"]/div[@class="wxTitle"]/div[@class="orgn"]/span | //div[@class="wxmain"]/div[@class="wxTitle"]/div[@class="orgnE"]/span ')
            units_1 = detail_con.xpath('/html/body/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/span')
            if len(units) != 0:
                name = []
                for unit in units:
                    name.append(unit.xpath('./a/text()')[0])
                item['unit'] = '|'.join(name)
            elif len(units_1) != 0:
                name = []
                for unit in units:
                    name.append(unit.xpath('./text()')[0])
                item['unit'] = '|'.join(name)
            else:
                item['unit'] = ''

            abstract = detail_con.xpath('//span[@id="ChDivSummary"]/text()')
            abstract_1 = detail_con.xpath('/html/body/div[1]/div[2]/div[1]/table/tbody/tr[7]/td[2]/text()')
            if len(abstract) != 0:
                item['abstract'] = abstract[0]
            elif len(abstract_1) != 0:
                item['abstract'] = abstract_1[0]
            else:
                item['abstract'] = ''

            keywords = detail_con.xpath('//div[@class="wxmain"]/div[@class="wxInfo"]/div[@class="wxBaseinfo"]/p[3]/a | //div[@class="wxmain"]/div[@class="wxInfo"]/div[@class="wxBaseinfo"]/p[2]/a | //*[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxInfo wxInfoEn"]/div/p[2]/a')
            keywords_1 = detail_con.xpath('/html/body/div[1]/div[2]/div[1]/table/tbody/tr[6]/td[2]/a')
            if len(keywords) != 0:
                key = []
                for keyword in keywords:
                    key.append(keyword.xpath('./text()')[0].replace(';', '').replace('；', '').strip())
                item['keywords'] = '|'.join(key)
            elif len(keywords_1) != 0:
                key = []
                for keyword in keywords:
                    key.append(keyword.xpath('./text()'))
                item['keywords'] = '|'.join(key)
            else:
                item['keywords'] = ''

            item['classify'] = detail_con.xpath('//div[@class="wxmain"]/div[@class="wxInfo"]/div[@class="wxBaseinfo"]/p[4]/text()')
            if len(item['classify']) == 0:
                item['classify'] = ''
            else:
                item['classify'] = item['classify'][0]

            item['url'] = url_detail

            print(item)
            self.save_data(item)

            time.sleep(2)

    def save_data(self,item):
        self.cur.execute(
            """insert into zhiwang (title,author,unit,abstract,keywords,classify,url) values (%s,%s,%s,%s,%s,%s,%s)""",
            (
                item['title'],
                item['author'],
                item['unit'],
                item['abstract'],
                item['keywords'],
                item['classify'],
                item['url'],
            ))
        self.conn.commit()

    def main(self):
        self.get_in()
        self.get_list()


if __name__ == '__main__':
    key_word = 'python'
    zw = Zhiwang(key_word)
    zw.main()
