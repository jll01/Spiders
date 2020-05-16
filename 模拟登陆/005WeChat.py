#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   WeChat.py
# @Time    :   2019/6/29 10:03
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

import requests
import time
import re
import urllib3
import json

from PIL import Image

# 禁止requests检查ssl ca证书警告
urllib3.disable_warnings()


class Login(object):
    '''微信网页二维码模拟登陆'''
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
        }
        self.session = requests.session()

    def get_uuid(self):
        '''获取uuid，链接重定向时需要的参数'''
        login_url = 'https://login.wx.qq.com/jslogin'
        params = {
            'appid': 'wx782c26e4c19acffb',
            'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
            'fun': 'new',
            'lang': 'zh_CN',
            '_': int(time.time() * 1000),  # 时间戳
        }
        # params是get请求方式中用来传输传参的
        response = self.session.get(login_url, headers=self.headers, params=params, verify=False).text
        # 获取uuid
        self.get_uuid_code, self.uuid = re.findall(r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(.*?)";',response)[0]

    def get_QRImage(self):
        '''获取二维码'''
        QR_code = 'https://login.weixin.qq.com/qrcode/%s' % self.uuid
        QR = self.session.get(QR_code, headers=self.headers, verify=False).content
        with open('QRImage.jpg', 'wb') as f:
            f.write(QR)
        time.sleep(0.5)
        im = Image.open('QRImage.jpg')
        im.show()
        im.close()
        print('请使用微信扫描二维码登录')

    def checklogin(self):
        '''手机扫描登陆'''
        url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=%s&tip=1&_=%d' % (self.uuid, time.time()*1000)
        # 用来限制当self.check_code='201'时打印次数，
        num = 0
        # 以轮询的方式判断手机是否扫描确认
        while True:
            login = self.session.get(url, headers=self.headers, verify=False).content.decode('utf-8')
            # 提取判断扫描的code
            self.check_code = re.findall(r'window.code=(\d+);', login)[0]
            #当self.check_code == '201'并且num=0的时候打印
            if self.check_code == '201' and num == 0:  # 已扫描
                print('成功扫描,请在手机上点击确认登录')
                # 只打印一次
                num = 1
            # 扫描并在手机上确认登陆
            elif self.check_code == '200' and num == 1:  # 已扫描
                print('正在登录中...')
                # 提取重定向来凝结
                self.redirect_uri = re.findall(r'window.redirect_uri="(\S+?)";', login)[0]
                break
            elif self.check_code == '408':  # 超时
                print('超时')
                break
            time.sleep(1)
        return self.check_code

    def login(self):
        '''重定向登陆链接'''
        response = self.session.get(self.redirect_uri + '&fun=new&version=v2', headers=self.headers, verify=False).text
        # 正则提取登陆所需参数
        self.skey = re.findall(r'<skey>(.*?)</skey>', response)[0]
        self.pass_ticket = re.findall(r'<pass_ticket>(.*?)</pass_ticket>', response)[0]
        self.isgrayscale = re.findall(r'<isgrayscale>(.*?)</isgrayscale>', response)[0]
        print('登陆成功！')

    def get_content(self):
        '''获取信息'''
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket={}&r={}&seq=0&skey={}'.format(self.pass_ticket, int(time.time()*1000), self.skey)
        userinfo = self.session.get(url, headers=self.headers, verify=False).content
        info_json = json.loads(userinfo)
        list_friends = info_json['MemberList']

        good_friends = []   # 好友
        group_chats = []   # 群聊
        official_accounts = []  # 官方服务号
        personal_accounts = []  # 公众号

        print('通讯录共%s位好友' % info_json['MemberCount'])
        # 循环获取分类
        for friend in list_friends:
            # 性别
            sex = '未知' if friend['Sex'] == 0 else '男' if friend['Sex'] == 1 else '女'
            # 用来保存满足条件的一条信息
            item = {}
            # 群聊的friend['VerifyFlag'] == 0并且UserName中包含@@
            if friend['VerifyFlag'] == 0 and friend['UserName'].find('@@') == 0:
                item['NickName'] = friend['NickName']
                group_chats.append(item)
            # 好友的friend['VerifyFlag'] == 0并且UserName中不包含@@
            elif friend['VerifyFlag'] == 0 and friend['UserName'].find('@@') == -1:
                item['NickName'] = friend['NickName']
                item['Sex'] = sex
                item['RemarkName'] = friend['RemarkName']
                item['Signature'] = friend['Signature']
                item['Addr'] = friend['Province'] + friend['City']
                good_friends.append(item)
            # 官方性的服务号
            elif friend['VerifyFlag'] == 24:
                item['NickName'] = friend['NickName']
                item['Signature'] = friend['Signature']
                item['Addr'] = friend['Province'] + friend['City']
                official_accounts.append(item)
            # 个人公众号
            elif friend['VerifyFlag'] == 8:
                item['NickName'] = friend['NickName']
                item['Signature'] = friend['Signature']
                item['Addr'] = friend['Province'] + friend['City']
                personal_accounts.append(item)
        print('服务号:{}'.format(official_accounts))
        print('公众号:{}'.format(personal_accounts))
        print('群聊:{}'.format(group_chats))
        print('好友:{}'.format(good_friends))

    def main(self):
        self.get_uuid()
        self.get_QRImage()
        code = self.checklogin()
        # 手机确认登陆后才能执行下一步
        if code == '200':
            self.login()
            self.get_content()


if __name__ == '__main__':
    l = Login()
    l.main()