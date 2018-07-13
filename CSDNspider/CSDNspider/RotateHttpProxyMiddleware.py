#!/usr/bin/python
#-*-coding:utf-8-*-

import random
from scrapy.conf import settings
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware


class RotateHttpProxyMiddleware(HttpProxyMiddleware):
    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        thisip = random.choice(settings['IPPOOL'])
        print ("当前使用的IP是：" + thisip['ipaddr'])
        request.meta['proxy'] = 'http://' + thisip['ipaddr']