# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request

from CSDNspider.items import UserItem, CodeItem, QAquestionItem, QAanswerItem
from CSDNspider.database.DB_mysql import DB_mysql


class Userspider(scrapy.Spider):
    name = 'user_spider'
    allowed_domains = ['my.csdn.net']
    start_urls = []

    sql = 'select userID from author where user_crawl = 0'
    dbquery = DB_mysql()
    result = dbquery.query(sql)
    for userID in result:
        start_urls.append('http://my.csdn.net/' + userID[0])

    def parse(self, response):
        separator = re.compile('((\\n|\\t|\\r|( ))+( )*)+')
        useritem = UserItem()
        detail_str = ''
        focus_str = ''
        befoucs_str = ''

        dbupdate = DB_mysql()
        dbupdate.update(response.url.split('/')[-1], 2)

        useritem['userID'] = response.url.split('/')[-1]
        useritem['link'] = response.url
        useritem['nickname'] = response.xpath('//dt[@class="person-nick-name"]/span/text()').extract()[0]

        for detail in response.xpath('//dd[@class="person-detail"]/text()').extract()[:-1]:
            detail_str = detail_str + separator.sub('', detail) + ','
        useritem['detail'] = detail_str[:-1]

        useritem['sign'] = response.xpath('//dd[@class="person-sign"]/text()').extract()[0]
        #useritem['scores_label'] =
        useritem['number_focus'] = int(response.xpath('//div[@class="focus"]/div[1]/span/text()').extract()[0])
        useritem['number_befoucs'] = int(response.xpath('//div[@class="focus beFocus"]/div[1]/span/text()').extract()[0])

        for focus_user in response.xpath('//div[@class="focus"]/div[2]//@href').extract():
            focus_str = focus_str + focus_user + ','
        useritem['focus_userID'] = focus_str[:-1]

        for befocus_user in response.xpath('//div[@class="focus beFocus"]/div[2]//@href').extract():
            befoucs_str = befoucs_str + befocus_user + ','
        useritem['befocus_userID'] = befoucs_str[:-1]

        yield useritem

