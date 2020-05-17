#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   ip_pool.py
# @Time    :   2019/11/26 16:25
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import requests
import random
import urllib3
import re
import json


from lxml import etree

urllib3.disable_warnings()


def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    ]
    UserAgent = random.choice(user_agent_list)
    headers = {'User-Agent': UserAgent}
    return headers


def get_ip():
    page = 1
    # proxy = [
    #     'http://113.120.36.104:808',
    #     'http://58.253.70.149:8080',
    # ]
    # proxy_li= random.choice(proxy)
    # proxies = {re.match(r'(.*)://',proxy_li)[1]:proxy_li}

    while page <= 10:
        url = 'https://www.xicidaili.com/nn/%d' % page
        response = requests.get(url,headers=get_headers(),verify=False).text
        html = etree.HTML(response)
        get_ip_list = html.xpath('//div[@id="body"]/table[@id="ip_list"]//tr')
        for con in get_ip_list[1:]:
            ip = con.xpath('./td[2]/text()')[0]
            port = con.xpath('./td[3]/text()')[0]
            ip_type = con.xpath('./td[6]/text()')[0]
            ip_time = con.xpath('./td[9]/text()')[0]

            if ip_type.lower() in ['http', 'https'] and ip_time[-1] in ['时', '天']:
                ip_url = ip_type.lower() + '://' + ip + ':' + port
                proxies = {
                    ip_type.lower(): ip_url
                }
                ip_list.append(proxies)
        page += 1

    write_ip()


def check_ip():
    proxies = read_ip()
    url = 'http://icanhazip.com/'
    for proxy in proxies:
        try:
            code = requests.get(url,headers=get_headers(),proxies=proxy,timeout=1.5,verify=False).status_code
        except:
            if proxy in ip_list:
                ip_list.remove(proxy)
            print('%s验证失败！' % proxy)
        else:
            if code == 200 and proxy not in ip_list:
                ip_list.append(proxy)
                print('%s验证成功！' % proxy)
    write_ip()


def write_ip():
    with open('ip.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(ip_list, ensure_ascii=False))


def read_ip():
    with open('ip.json', 'r') as f:
        return json.loads(f.read())


if __name__ == '__main__':
    ip_list = []
    get_ip()
    check_ip()
    print(ip_list)
