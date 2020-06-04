#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   006renrencookiejar.py
# @Time    :   2019/11/26 20:55
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import urllib.request
import http.cookiejar
from urllib import parse

cookie = http.cookiejar.CookieJar()
cookie_handle = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(cookie_handle)
my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 7.0; Win64; x64) '
    }
url = 'http://www.renren.com/PLogin.do'

data = {
    'email':'****',
    'password':'****',
}
data = parse.urlencode(data).encode('utf-8')
req = urllib.request.Request(url,headers=my_headers,data=data)
con = opener.open(req).read()
print(con.decode('utf-8'))
