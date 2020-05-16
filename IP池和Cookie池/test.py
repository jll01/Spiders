#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   mongo_test.py
# @Time    :   2019/7/10 22:08
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import json

list_test = [
    {'http': 'http://182.34.35.83:9999'},
    {'https': 'https://124.93.201.59:59618'},
    {'https': 'https://218.24.16.198:43620'},
    {'https': 'https://183.6.183.35:8010'},
    {'https': 'https://113.121.22.176:9999'},
    {'https': 'https://113.12.202.50:40498'},
    {'https': 'https://1.197.204.14:9999'},
    {'https': 'https://222.189.191.112:9999'},
    {'http': 'http://113.120.36.104:808'},
    {'https': 'https://117.91.232.167:9999'},
    {'https': 'https://114.239.148.87:808'},
    {'https': 'https://115.53.37.158:9999'},
    {'https': 'https://117.91.232.44:9999'},
    {'https': 'https://183.63.101.62:53281'},
    {'https': 'https://222.89.32.172:9999'},
    {'https': 'https://113.121.20.64:808'},
    {'https': 'https://113.121.22.253:9999'},
    {'https': 'https://113.121.23.93:9999'},
    {'https': 'https://222.89.32.154:9999'},
    {'https': 'https://58.58.213.55:8888'},
    {'https': 'https://1.198.73.204:9999'},
    {'https': 'https://110.189.152.86:52277'},
    {'http': 'http://119.138.225.41:8118'},
    {'http': 'http://58.253.70.149:8080'},
    {'https': 'https://218.76.253.201:61408'},
    {'https': 'https://120.83.102.105:808'},
    {'https': 'https://120.79.147.254:9000'},
    {'https': 'https://211.147.239.101:57281'},
    {'https': 'https://27.195.216.24:8118'},
    {'https': 'https://60.190.250.120:8080'},
    {'https': 'https://113.124.87.161:53128'},
    {'https': 'https://221.6.138.154:30893'},
    {'https': 'https://1.198.72.247:9999'},
    {'https': 'https://1.192.241.154:9999'},
    {'https': 'https://59.32.37.249:61234'},
    {'https': 'https://114.225.171.86:53128'},
    {'https': 'https://182.34.33.58:808'},
    {'https': 'https://1.197.203.20:9999'}
]

with open('test.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(list_test))

with open('test.json', 'r') as f_r:
    con = f_r.read()

print(type(eval(con)))
