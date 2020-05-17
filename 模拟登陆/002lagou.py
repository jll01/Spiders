#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   lagou.py
# @Time    :   2019/11/26 11:16
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import requests
import hashlib
import re, time

#请求对象
session = requests.session()

#请求头信息
HEADERS = {
    'Referer': 'https://passport.lagou.com/login/login.html',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:51.0) Gecko/20100101 Firefox/51.0',
}


def get_password(passwd):
    '''这里对密码进行了md5双重加密 veennike 这个值是在main.html_aio_f95e644.js文件找到的 '''
    passwd = hashlib.md5(passwd.encode('utf-8')).hexdigest()
    passwd = 'veenike' + passwd + 'veenike'
    passwd = hashlib.md5(passwd.encode('utf-8')).hexdigest()
    return passwd

def get_token():
    Forge_Token = ""
    Forge_Code = ""
    login_page = 'https://passport.lagou.com/login/login.html'
    data = session.get(login_page, headers=HEADERS)
    match_obj = re.match(r'.*X_Anti_Forge_Token = \'(.*?)\';.*X_Anti_Forge_Code = \'(\d+?)\'', data.text, re.DOTALL)
    if match_obj:
        Forge_Token = match_obj.group(1)
        Forge_Code = match_obj.group(2)
    return Forge_Token, Forge_Code


def login(username, passwd):
    X_Anti_Forge_Token, X_Anti_Forge_Code = get_token()
    login_headers = HEADERS.copy()
    login_headers.update({'X-Requested-With': 'XMLHttpRequest', 'X-Anit-Forge-Token': X_Anti_Forge_Token, 'X-Anit-Forge-Code': X_Anti_Forge_Code})
    postData = {
            'isValidate': 'true',
            'username': username,
            'password': get_password(passwd),
            'request_form_verifyCode': get_captcha(),
            'submit': '',
            'challenge': '',
    }
    response = session.post('https://passport.lagou.com/login/login.json', data=postData, headers=login_headers)
    print(response.text)


def get_cookies():
    return requests.utils.dict_from_cookiejar(session.cookies)


def get_captcha():
    url = 'https://passport.lagou.com/vcode/create?from=register&refresh={}'.format(str(int(time.time() * 1000)))
    response = session.get(url, headers=HEADERS)
    with open('captcha.jpg', 'wb') as f:
        f.write(response.content)

    from PIL import Image
    try:
        captcha_image = Image.open('captcha.jpg')
        captcha_image.show()
        captcha_image.close()
    except:
        print('captcha.jpg not found!')
    code = input('please check the captcha code and enter it:')
    return code


if __name__ == "__main__":
    username = "17762269549"
    passwd = "qupinljl125boba"
    login(username, passwd)
    print(get_cookies())