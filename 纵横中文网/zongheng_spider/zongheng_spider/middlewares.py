# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent


class RandomUserAgent(object):
    def process_request(self, request, spider):
        useragent = UserAgent().random
        request.headers.setdefault('User-Agent', useragent)
