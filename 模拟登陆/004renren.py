#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   004renren.py
# @Time    :   2019/11/25 18:20
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests

sess = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
data = {
    "email":'18873561962',
    "password":"haijidema125821",
}

sess.post('http://www.renren.com/PLogin.do',headers=headers,data=data)

res = sess.get('http://www.renren.com/971271882/profile')
print(res.text)
with open('renren.html','w', encoding='utf-8') as f:
    f.write(res.text)
