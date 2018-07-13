# -*- coding: utf-8 -*-
import json
import re
import scrapy
from scrapy import Selector, Request

from CSDNspider.items import BlogItem, BlogCommentItem, CodeItem, UserItem, AuthorItem, QAquestionItem, QAanswerItem
from CSDNspider.database.DB_mysql import DB_mysql


class Testspider(scrapy.Spider):
    name = 'test'
    start_urls = ['http://bbs.csdn.net/topics/392189417']

    def parse(self, response):
        separator = re.compile('((\\n|\\t|\\r|( ))+( )*)+')
        if not re.search('page', response.url):
            start_floor = 2
        else:
            start_floor = 0
        print start_floor
        for reply in response.xpath('//div[@class="detailed"]//table')[start_floor:]:
            print '---------'
            print int(re.sub(r'\D', "", reply.xpath('descendant::span[@class="fr"]/text()').extract()[1]))
            print '---------'


















