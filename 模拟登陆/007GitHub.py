#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   007GitHub.py
# @Time    :   2019/11/28 8:47
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
from lxml import etree


def get_token(login_url, header, sess):

    res = sess.get(login_url,headers=header, verify=False)

    con = etree.HTML(res.text)
    token = con.xpath('//*[@id="login"]//input[2]/@value')
    return token


def Git_Login(email,password):
    sess = requests.Session()
    header = {
        'Refer': 'https://github.com',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36",
        'Host': 'github.com',
    }

    login_url = 'https://github.com/login'
    post_url = 'https://github.com/session'

    post_data = {
        'commit': 'Sign in',
        'utf-8': '✓',
        'authenticity_token': get_token(login_url, header, sess),
        'login': email,
        'password': password
    }

    response = sess.post(post_url,headers=header,data=post_data,verify=False)
    print(response.text)

    with open('GitHub.html', 'w', encoding='utf-8') as f:
        f.write(response.text)



if __name__ == '__main__':
    Git_Login('username', 'passwd')
