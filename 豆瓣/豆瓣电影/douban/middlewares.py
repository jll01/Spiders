# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from scrapy.conf import settings
import base64


class RandomUserAgent(object):

    def process_request(self, request, spider):
        useragent = random.choice(settings['USER_AGENTS'])
        request.headers.setdefault('User-Agent', useragent)


class RandomProxy(object):

    def process_request(self, request, spider):
        proxy = random.choice(settings['PROXIES'])
        if len(proxy['user_password']) == 0:
            request.meta['proxy'] = "http://" + proxy['ip_port']
        else:
            base64_userpassword = base64.b64encode(proxy['user_password'])
            request.meta['proxy'] = "http://" + proxy['ip_port']
            request.headers['Proxy-Authorization'] = 'Basic' + base64_userpassword
