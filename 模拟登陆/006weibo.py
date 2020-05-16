#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   weibo.py
# @Time    :   2019/6/26 9:06
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import time
import base64
import rsa
import binascii
import requests
import re
import random
import urllib3
import json

from PIL import Image
from urllib.parse import quote_plus, unquote
from lxml import etree

# 禁止requests发送请求时检查证书错误(InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised.)
urllib3.disable_warnings()


class SinaWeibo_Login(object):
    '''新浪微博模拟登陆'''
    def __init__(self,username,password):
        self.username = username
        self.password = password
        # 创建session对象，可以保存Cookie值
        self.session = requests.session()
        # Cookie值，保存在ssion里
        self.session.get('http://weibo.com/login.php', verify=False)
        # 处理headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
        # self.proxies = {
        #     'https': 'https://163.204.241.19:9999',
        #     'http': 'http://121.15.254.156:888',
        # }

    def get_su(self):
        '''对用户名编码'''
        username_base64 = base64.b64encode(quote_plus(self.username).encode("utf-8"))
        return username_base64.decode("utf-8")

    def get_other_info(self):
        '''登陆前需要的参数获取servertime、nonce、pubkey和rsakv等'''
        url_pre = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=%d" % (self.get_su(), int(time.time()*1000))
        # self.session包含用户的Cookie值
        res = self.session.get(url_pre, headers=self.headers, verify=False).text
        self.res_json = eval(re.findall(r'({.*})', res)[0])

        self.servertime = self.res_json.get('servertime', 'not find in res_json')
        self.nonce = self.res_json.get('nonce', 'not find in res_json')
        self.pubkey = self.res_json.get('pubkey', 'not find in res_json')
        self.rsakv  = self.res_json.get('rsakv', 'not find in res_json')

    def get_password(self):
        '''对密码进行加密操作'''
        publickey = rsa.PublicKey(int(self.pubkey, 16), int('10001', 16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        sp = rsa.encrypt(message.encode("utf-8"), publickey)
        return binascii.b2a_hex(sp)

    def captcha(self):
        '''获取验证码'''
        cap_url = "http://login.sina.com.cn/cgi/pin.php?r={}&s=0&p={}".format(int(random.random() * 10**8), self.res_json['pcid'])
        cap_page = self.session.get(cap_url, headers=self.headers, verify=False)
        with open("captcha.jpg", 'wb') as f:
            f.write(cap_page.content)

        im = Image.open("captcha.jpg")
        im.show()
        im.close()

    def get_post_data(self):
        '''登陆时需要的post数据'''
        post_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1',
            'vsnf': '1',
            'su': self.get_su(),
            'service': 'miniblog',
            'servertime': self.servertime,
            'nonce': self.nonce,
            'pwencode': 'rsa2',
            'rsakv': self.rsakv,
            'sp': self.get_password(),
            'sr': '1536*864',
            'encoding': 'UTF-8',
            'prelt': '493',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }

        # 判断是否需要输入验证码
        if self.res_json['showpin'] != 0:
            self.captcha()
            post_data['door'] = input("请输入验证码:")
        return post_data

    def login(self):
        '''登陆微博'''
        # 预登陆需要的参数获取
        self.get_other_info()

        # 登陆的url
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        login_page = self.session.post(url, data=self.get_post_data(), headers=self.headers, verify=False)
        login_loop = (login_page.content.decode("GBK"))

        # 在获取的页面中通过正则表达式匹配提取重定向的url
        refer_url = re.findall(r'location\.replace\([\'"](.*?)[\'"]\)', login_loop)[0]

        ret = re.findall(r'retcode=(\d+)', unquote(refer_url))[0]

        if ret == '0':
            # 请求重定向url，在获取的页面通过正则匹配获取下一个链接所需要的参数ticket, ssosavestate
            refer_index = self.session.get(refer_url, headers=self.headers, verify=False).text
            if re.findall(r'"retcode":(\d+)', refer_index)[0] == '0':
                ticket, ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"', refer_index)[0]
                # 登陆
                login_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(
                    ticket, ssosavestate, int(time.time()*1000))
                # 获取uniqueid(相当于登陆账号的id号)
                get_uid = self.session.get(login_url, verify=False).text
                uid = re.findall(r'"uniqueid":"(.*?)"', get_uid)[0]

                # 登陆账号的主页链接
                home_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uid
                # home_url = 'https://weibo.com/u/%s/home?wvr=5&lf=reg' % uid
                weibo_page = self.session.get(home_url, headers=self.headers, verify=False).content

                # 将获取的主页写入文件保存
                with open('home.html', 'wb') as f:
                    f.write(weibo_page)

                # 匹配登陆账号的昵称
                userID = re.findall(r'<title>(.*?)</title>', weibo_page.decode("utf-8", 'ignore'), re.S)[0]

                print("欢迎你 %s, 登陆成功" % userID)

                current_page = 0
                pagebar = 0
                pre_page = 0

                while True:
                    spider_url = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803_ctg1_2288_-_ctg1_2288&from=faxian_hot&mod=fenlei&pagebar={}&tab=home&current_page={}&pre_page={}&page=1&pl_name=Pl_Core_NewMixFeed__3&id=102803_ctg1_2288_-_ctg1_2288&script_uri=/102803_ctg1_2288_-_ctg1_2288&feed_type=1&domain_op=102803_ctg1_2288_-_ctg1_2288&__rnd={}'.format(
                        pagebar, current_page, pre_page, int(time.time() * 1000))

                    json_data = json.loads(self.session.get(spider_url, headers=self.headers, verify=False).text)

                    if len(re.findall(r'<!-- 用户信息为空微博被删除，赞过的feed列表显示被删除的微博 -->', str(json_data))) != 0:
                        data_content = etree.HTML(json_data['data'])
                        WB_feed_detail = data_content.xpath('//div[@class="WB_feed_detail clearfix"]//div[@class="WB_detail"]')
                        WB_feed_handl = data_content.xpath('//div[@class="WB_feed_handle"]')

                        item = {}
                        for i in range(len(WB_feed_detail)):
                            item['nickname']= WB_feed_detail[i].xpath('./div[@class="WB_info"]/a[1]/text()')[0].strip()
                            item['home_url'] = WB_feed_detail[i].xpath('./div[@class="WB_info"]/a[1]/@href')[0]
                            item['create_time'] = WB_feed_detail[i].xpath('./div[@class="WB_from S_txt2"]/a[1]/@title')[0]
                            item['wb_detail'] = WB_feed_detail[i].xpath('./div[@class="WB_from S_txt2"]/a[1]/@href')[0]
                            tool = WB_feed_detail[i].xpath('./div[@class="WB_from S_txt2"]/a[2]/text()')
                            if len(tool) != 0:
                                item['tool'] = tool[0]
                            else:
                                item['tool'] = '已隐藏'
                            item['content_detail'] = WB_feed_detail[i].xpath('./div[@class="WB_text W_f14"]')[0].text.strip()
                            image_urls = WB_feed_detail[i].xpath('.//div[@class="media_box"]/ul/li')
                            video_urls = WB_feed_detail[i].xpath('.//div[@class="media_box"]/ul/li//div[2]//video[@class="wbv-tech"]/@src')
                            # print(len(video_urls), video_urls)
                            item['image_url'] = []
                            if len(image_urls) > 0:
                                for image_url in image_urls:
                                    item['image_url'].extend(image_url.xpath('./img/@src'))
                                    # item['image_url'].append(image_url)
                            # elif len(video_urls) > 0:
                            #     item['video_url'] = []
                            #     for video_url in video_urls:
                            #         # item['media_url'].extend(media_url.xpath('./img/@src'))
                            #         item['video_url'].append(video_url)
                            # else:
                            #     item['media_url'] = []
                            # 转发数
                            item['share_num'] = (WB_feed_handl[i].xpath('.//li[2]//span[@class="pos"]//em[2]/text()')[0])
                            if item['share_num'].strip().isdigit():
                                item['share_num'] = int(item['share_num'])
                            else:
                                item['share_num'] = 0
                            # 评论数
                            item['comments_num'] = (WB_feed_handl[i].xpath('.//li[3]//span[@class="pos"]//em[2]/text()')[0])
                            if item['comments_num'].strip().isdigit():
                                item['comments_num'] = int(item['comments_num'])
                            else:
                                item['comments_num'] = 0
                            # 点赞数
                            item['ok_num'] = (WB_feed_handl[i].xpath('.//li[4]//span[@class="pos"]//em[2]/text()')[0])
                            if item['ok_num'].strip().isdigit():
                                item['ok_num'] = int(item['ok_num'])
                            else:
                                item['ok_num'] = 0

                            with open('data.json', 'a', encoding='utf-8') as f:
                                f.write(json.dumps(item, ensure_ascii=False) + ',\n')
                        if current_page < 99:
                            current_page += 1
                            pagebar = current_page - 1
                            pre_page = 1
                        else:
                            break
                    else:
                        break
            else:
                print('重定向https://passport.weibo.com失败！')
        else:
            print('验证码错误！登陆失败！')


if __name__ == '__main__':
    username = '18873561962'
    password = 'haijidema'
    login = SinaWeibo_Login(username,password)
    login.login()

