# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector, Request

from CSDNspider.items import UserItem, AuthorItem
from CSDNspider.database import DB_mysql

class Blogspider(scrapy.Spider):
    name = 'blog_column_spider'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['http://blog.csdn.net/column.html']

    def parse(self, response):
        for category in response.xpath('//div[@class="blog_category"]/descendant::a/@href').extract():
            category_url = 'http://blog.csdn.net' + category
            #print (category_url)
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        for column in response.xpath('//div[@class="column_index clearfix"]/descendant::a/@href').extract():
            column_url = 'http://blog.csdn.net' + column
            #print column_url
            yield Request(column_url, callback=self.parse_column)
        if response.xpath('//div[@class="page_nav"]/a/text()').extract()[-2] == u'下一页':
            nextpage_url = 'http://blog.csdn.net' + response.xpath('//div[@class="page_nav"]/a/@href').extract()[-2]
            yield Request(nextpage_url, callback=self.parse_category)

    def parse_column(self, response):
        blog_url = response.xpath('//div[@class="ba_c"]//a[@tip="username"]/@href').extract()[0]
        user_id = blog_url.split('/')[-1]
        #print user_id
        dbcheck = DB_mysql()
        if dbcheck.check(user_id):
            authorItem = AuthorItem()
            authorItem['userID'] = user_id
            authorItem['link'] = blog_url
            authorItem['blog_crawl'] = 0
            authorItem['user_crawl'] = 0
            yield authorItem
