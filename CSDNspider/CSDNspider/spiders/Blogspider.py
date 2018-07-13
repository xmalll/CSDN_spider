# -*- coding: utf-8 -*-
import json
import re
import scrapy
from scrapy import Selector, Request

from CSDNspider.items import BlogItem, BlogCommentItem, CodeItem, UserItem, AuthorItem
from CSDNspider.database.DB_mysql import DB_mysql


class Blogspider(scrapy.Spider):
    name = 'blog_spider'
    allowed_domains = ['blog.csdn.net']
    start_urls = []

    sql = 'select userID from author where blog_crawl = 0'
    dbquery = DB_mysql()
    result = dbquery.query(sql)
    for userID in result:
        start_urls.append('http://blog.csdn.net/' + userID[0])

    def parse(self, response):
        dbupdate = DB_mysql()
        dbupdate.update(response.url.split('/')[-1], 1)
        yield Request(response.url, callback=self.parse_bloglist)

    def parse_bloglist(self, response):
        for url in response.xpath('//span[@class="link_title"]/descendant::a/@href').extract():
            blog_url = 'http://blog.csdn.net' + url
            #print blog_url
            yield Request(blog_url, callback=self.parse_blog)
        if response.xpath('//div[@class="pagelist"]/a/text()'):
            if response.xpath('//div[@class="pagelist"]/a/text()').extract()[-2] == u'下一页':
                nextpage_url = 'http://blog.csdn.net' + response.xpath('//div[@class="pagelist"]/a/@href').extract()[-2]
                # print nextpage_url
                yield Request(nextpage_url, callback=self.parse)

    def parse_blog(self, response):
        blogitem = BlogItem()
        separator = re.compile('((\\n|\\t|\\r|( ))+( )*)+')
        category_str = ' '
        content_str = ''
        count = 0

        blogitem['blogID'] = response.url.split('/')[-1]
        blogitem['userID'] = response.url.split('/')[-4]
        blogitem['link'] = response.url
        blogitem['title'] = separator.sub(' ', response.xpath('//div[@class="article_title"]//a/text()').extract()[-1])
        blogitem['time'] = response.xpath('//span[@class="link_postdate"]/text()').extract()[0]
        blogitem['number_read'] = int(re.sub(r'\D', "",  response.xpath('//span[@class="link_view"]/text()').extract()[0]))
        blogitem['number_comment'] = int(re.sub(r'\D', "", response.xpath('//span[@class="link_comments"]/text()').extract()[1]))
        blogitem['number_ding'] = int(re.sub(r'\D', "", response.xpath('//dl[@id="btnDigg"]/dd/text()').extract()[0]))
        blogitem['number_cai'] = int(re.sub(r'\D', "", response.xpath('//dl[@id="btnBury"]/dd/text()').extract()[0]))
        blogitem['article_type'] = response.xpath('//div[@class="article_title"]/span/@class').extract()[0].split('_')[-1]

        if response.xpath('//span [@class="link_categories"]/a//text()'):
            for category in response.xpath('//span [@class="link_categories"]/a//text()').extract():
                category_str = category_str + category + '/'
        blogitem['category'] = category_str[:-1]

        content_list = response.xpath('//div[@id="article_content"]//text()').extract()
        for content in content_list:
            content_str = content_str + content
        blogitem['content'] = content_str
        #print content_str.encode('GBK', 'ignore')
        
        blogitem['content_xml'] = response.xpath('//div[@id="article_content"]').extract()[0]

        yield blogitem

        if int(re.sub(r'\D', "", response.xpath('//span[@class="link_comments"]/text()').extract()[1])) > 0:
            comment_url = 'http://blog.csdn.net/' + response.url.split('/')[-4] + '/comment/list/' + response.url.split('/')[-1]
            #print comment_url
            yield Request(comment_url, callback=self.parse_blogcomment, meta={'author': response.url.split('/')[-4], 'link': response.url})

            if response.xpath('//pre').extract():
                for code in response.xpath('//pre'):
                    codeitem = CodeItem()
                    count = count + 1
                    codeitem['codeID'] = response.url.split('/')[-4] + response.url.split('/')[-1] + '_' + str(count)
                    codeitem['userID'] = response.url.split('/')[-4]
                    codeitem['link'] = response.url
                    if code.xpath('code/@class'):
                        codeitem['language'] = code.xpath('@class').extract()[0] + ' ' + code.xpath('code/@class').extract()[0]
                    elif code.xpath('@class'):
                        codeitem['language'] = code.xpath('@class').extract()[0]
                    else:
                        codeitem['language'] = ''
                    codeitem['code'] = ''.join(code.xpath('descendant::text()').extract())
                    yield codeitem

    def parse_blogcomment(self, response):
        blogcommentitem = BlogCommentItem()
        comment_list = json.loads(response.body)['list']

        for comment in comment_list:
            blogcommentitem['blogcommentID'] = comment['CommentId']
            blogcommentitem['userID'] = comment['UserName']

            blogcommentitem['link'] = response.meta['link']
            blogcommentitem['blogID'] = comment['ArticleId']
            blogcommentitem['authorID'] = response.meta['author']
            blogcommentitem['time'] = comment['PostTime']

            blogcommentitem['content'] = comment['Content']

            if re.findall(r'\[reply\]', comment['Content']):
                blogcommentitem['commenttoID'] = re.findall(r'\[reply\](.*)\[/reply\]', comment['Content'])[0]
            else:
                blogcommentitem['commenttoID'] = response.meta['author']

            yield blogcommentitem

            dbcheck = DB_mysql()
            if dbcheck.check(blogcommentitem['userID']):
                authorItem = AuthorItem()
                authorItem['userID'] = blogcommentitem['userID']
                authorItem['link'] = 'http://my.csdn.net/' + blogcommentitem['userID']
                authorItem['blog_crawl'] = 0
                authorItem['user_crawl'] = 0
                yield authorItem














