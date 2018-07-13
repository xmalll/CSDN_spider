# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request

from CSDNspider.items import BBSTopicItem, BBSPostItem, UserItem, BBSReplyItem, CodeItem, AuthorItem
from CSDNspider.database.DB_mysql import DB_mysql


class BBSspider(scrapy.Spider):
    name = 'bbs_spider'
    #download_delay = 1.75
    allowed_domains = ['bbs.csdn.net']
    start_urls = []

    sql = 'SELECT link FROM db_csdn.bbs_topic order by bbstopicID desc;'
    dbquery = DB_mysql()
    result = dbquery.query(sql)
    for bbs_link in result:
        start_urls.append(bbs_link[0])
        start_urls.append(bbs_link[0] + '/closed')

    def parse(self, response):
        post_list = response.xpath('//tr')
        for post in post_list[1:-1]:
            title = post.xpath('td[1]/a/text()').extract()[0]
            point = int(post.xpath('td[2]/text()').extract()[0])
            number_reply = int(post.xpath('td[4]/text()').extract()[0])
            update_time = post.xpath('td[5]//span/text()').extract()[0]

            yield Request('http://bbs.csdn.net' + post.xpath('td[1]/a/@href').extract()[0], callback=self.parse_bbs,
                          meta={'title': title, 'point': point, 'number_reply': number_reply, 'update_time': update_time})

        if response.xpath('//a[@class="next"]/@href'):
            nextpage_url = 'http://bbs.csdn.net' + response.xpath('//a[@class="next"]/@href').extract()[0]
            yield Request(nextpage_url, callback=self.parse)

    def parse_bbs(self, response):
        separator = re.compile('((\\n|\\t|\\r|( ))+( )*)+')
        start_floor = 0
        if not re.search('page', response.url):
            start_floor = 2
            bbspostitem = BBSPostItem()
            tag_str = ' '
            bbspostitem['bbspostID'] = response.url.split('/')[-1]

            bbspostitem['userID'] = response.xpath('//div[@class="detailed"]/table[1]//dd[@class="username"]/a/text()').extract()[0]

            dbcheck = DB_mysql()
            if dbcheck.check(bbspostitem['userID']):
                authorItem = AuthorItem()
                authorItem['userID'] = bbspostitem['userID']
                authorItem['link'] = 'http://my.csdn.net/' + bbspostitem['userID']
                authorItem['blog_crawl'] = 0
                authorItem['user_crawl'] = 0
                yield authorItem

            bbspostitem['link'] = response.url
            bbspostitem['title'] = response.meta['title']

            if response.xpath('//div[@class="detailed"]/table[1]//div[@class="tag"]/span/a/text()'):
                for tag in response.xpath('//div[@class="detailed"]/table[1]//div[@class="tag"]/span/a/text()').extract():
                    tag_str = tag_str + tag + '/'
            bbspostitem['tag'] = tag_str[:-1]

            bbspostitem['point'] = response.meta['point']
            bbspostitem['number_reply'] = response.meta['number_reply']
            bbspostitem['number_ding'] = int(
                re.sub(r'\D', "", response.xpath('//div[@class="detailed"]/table[1]//div[@class="fr"]/a[@class="red digg"]/text()').extract()[0]))
            bbspostitem['number_cai'] = int(
                re.sub(r'\D', "", response.xpath('//div[@class="detailed"]/table[1]//div[@class="fr"]/a[@class="bury"]/text()').extract()[0]))
            bbspostitem['time'] = re.findall(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', separator.sub(' ', ' '.join(response.xpath('//div[@class="detailed"]/table[1]//span[@class="time"]/text()').extract())))[0]
            bbspostitem['update_time'] = response.meta['update_time']
            bbspostitem['content'] = separator.sub(' ', ''.join(response.xpath('//div[@class="detailed"]/table[1]//div[@class="post_body"]/text()|//div[@class="detailed"]/table[1]//div[@class="post_body"]/a/text()').extract()))
            bbspostitem['content_xml'] = response.xpath('//div[@class="detailed"]/table[1]//div[@class="post_body"]').extract()[0]

            yield bbspostitem

            if response.xpath('//div[@class="detailed"]/table[1]//pre').extract():
                count = 0
                for code in response.xpath('//div[@class="detailed"]/table[1]//pre'):
                    codeitem = CodeItem()
                    codeitem['codeID'] = bbspostitem['userID'] + bbspostitem['bbspostID'] + '_' + str(count)
                    codeitem['userID'] = bbspostitem['userID']
                    codeitem['link'] = bbspostitem['link']
                    if code.xpath('@class').extract():
                        codeitem['language'] = code.xpath('@class').extract()[0]
                    else:
                        codeitem['language'] = ''
                    codeitem['code'] = code.xpath('text()').extract()
                    yield codeitem
                    count = count + 1

        for reply in response.xpath('//div[@class="detailed"]//table')[start_floor:]:
            bbsreplyitem = BBSReplyItem()
            bbsreplyitem['bbsreplyID'] = reply.xpath('@id').extract()[0].split('-')[-1]
            bbsreplyitem['userID'] = reply.xpath('descendant::dd[@class="username"]/a/text()').extract()[0]

            dbcheck = DB_mysql()
            if dbcheck.check(bbsreplyitem['userID']):
                authorItem = AuthorItem()
                authorItem['userID'] = bbsreplyitem['userID']
                authorItem['link'] = 'http://my.csdn.net/' + bbsreplyitem['userID']
                authorItem['blog_crawl'] = 0
                authorItem['user_crawl'] = 0
                yield authorItem

            bbsreplyitem['link'] = response.url + reply.xpath('descendant::span[@class="fr"]/a/@href').extract()[0]

            if re.search('page', response.url):
                bbsreplyitem['replytoID'] = response.meta['replytoID']
            else:
                bbsreplyitem['replytoID'] = bbspostitem['userID']

            bbsreplyitem['score'] = int(re.sub(r'\D', "", reply.xpath('descendant::span[@class="fr"]/text()').extract()[1]))

            if reply.xpath('descendant::div[@class="fr"]/a[@class="red digg"]'):
                bbsreplyitem['number_ding'] = int(re.sub(r'\D', "", reply.xpath('descendant::div[@class="fr"]/a[@class="red digg"]/text()').extract()[0]))
            else:
                bbsreplyitem['number_ding'] = 0

            if reply.xpath('descendant::div[@class="fr"]/a[@class="bury"]'):
                bbsreplyitem['number_cai'] = int(re.sub(r'\D', "", reply.xpath('descendant::div[@class="fr"]/a[@class="bury"]/text()').extract()[0]))
            else:
                bbsreplyitem['number_cai'] = 0

            bbsreplyitem['time'] = re.findall(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', separator.sub(' ', ' '.join(reply.xpath('descendant::span[@class="time"]/text()').extract())))[0]
            bbsreplyitem['content'] = separator.sub(' ', ''.join(reply.xpath('descendant::div[@class="post_body"]/text()|descendant::div[@class="post_body"]/a/text()').extract()))
            bbsreplyitem['content_xml'] = reply.xpath('descendant::div[@class="post_body"]').extract()[0]

            yield bbsreplyitem

            if reply.xpath('descendant::pre').extract():
                count = 0
                for code in reply.xpath('descendant::pre'):
                    codeitem = CodeItem()
                    codeitem['codeID'] = bbsreplyitem['userID'] + bbsreplyitem['bbsreplyID'] + '_' + str(count)
                    codeitem['userID'] = bbsreplyitem['userID']
                    codeitem['link'] = bbsreplyitem['link']
                    if code.xpath('@class').extract():
                        codeitem['language'] = code.xpath('@class').extract()[0]
                    else:
                        codeitem['language'] = ''
                    codeitem['code'] = code.xpath('text()').extract()[0]
                    yield codeitem
                    count = count + 1

        if response.xpath('//a[@class="next"]/@href'):
            nextpage_url = 'http://bbs.csdn.net' + response.xpath('//a[@class="next"]/@href').extract()[0]
            yield Request(nextpage_url, callback=self.parse_bbs, meta={'replytoID': bbspostitem['userID']})













