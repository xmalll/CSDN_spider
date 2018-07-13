# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request

from CSDNspider.items import UserItem, CodeItem, QAquestionItem, QAanswerItem, AuthorItem
from CSDNspider.database.DB_mysql import DB_mysql


class QAspider(scrapy.Spider):
    name = 'qa_spider'
    allowed_domains = ['ask.csdn.net']
    start_urls = ['http://ask.csdn.net']

    def parse(self, response):
        separator = re.compile('((\\n|\\t|\\r|( ))+( )*)+')
        count = 0
        for question in response .xpath('//div[@class="questions_detail_con"]'):
            question_url = question.xpath('descendant::dl//@href').extract()[0]
            asker = question.xpath('descendant::a[@class="user_name"]/text()').extract()[0]
            word = u'个人悬赏'
            if question.xpath('descendant::a[@title="%s"]' % word):
                point = separator.sub('', question.xpath('descendant::a[@title="%s"]/text()' % word).extract()[0])
            else:
                point = '0'
            number_answer = int(response.xpath('//a[@class="answer_num "]/span/text()|//a[@class="answer_num disable_color"]/span/text()').extract()[count])
            number_read = int(re.sub(r'\D', "", response.xpath('//em[@class="browse"]/text()').extract()[count]))
            number_collect = int(re.sub(r'\D', "", response.xpath('//em[@class="collection"]/text()').extract()[count]))
            number_alsoask = int(re.sub(r'\D', "", response.xpath('//em[@class="focusit"]/text()').extract()[count]))
            answer_accepted = question.xpath('a/@title').extract()[0]
            yield Request(question_url, callback=self.parse_question, meta={'user': asker, 'point': point, 'number_answer': number_answer, 'number_read': number_read, 'number_collect': number_collect, 'number_alsoask': number_alsoask, 'answer_accepted': answer_accepted})
            count = count + 1

        if response.xpath('//a[@rel="next"]'):
            nextpage_url = 'http://ask.csdn.net' + response.xpath('//a[@rel="next"]/@href').extract()[0]
            print nextpage_url
            yield Request(nextpage_url, callback=self.parse)

    def parse_question(self, response):
        separator = re.compile('((\\n|\\t|\\r|( ))+( )*)+')
        askerID = ''
        answer_accepted = True

        if not re.search('page', response.url):
            qaquestionitem = QAquestionItem()
            tag_str = ' '

            qaquestionitem['qaquestionID'] = response.url.split('/')[-1]
            qaquestionitem['userID'] = response.meta['user']
            askerID = qaquestionitem['userID']

            dbcheck = DB_mysql()
            if dbcheck.check(qaquestionitem['userID']):
                authorItem = AuthorItem()
                authorItem['userID'] = qaquestionitem['userID']
                authorItem['link'] = 'http://my.csdn.net/' + qaquestionitem['userID']
                authorItem['blog_crawl'] = 0
                authorItem['user_crawl'] = 0
                yield authorItem

            qaquestionitem['link'] = response.url
            qaquestionitem['title'] = response.xpath('//div[@class="questions_detail_con"]//dt/text()').extract()[0]

            if response.xpath('//div[@class="tags"]/a/text()'):
                for tag in response.xpath('//div[@class="tags"]/a/text()').extract():
                    tag_str = tag_str + tag + '/'
                qaquestionitem['tag'] = tag_str[:-1]
            else:
                qaquestionitem['tag'] = ''

            qaquestionitem['point'] = response.meta['point']
            qaquestionitem['number_answer'] = response.meta['number_answer']
            qaquestionitem['number_read'] = response.meta['number_read']
            qaquestionitem['number_collect'] = response.meta['number_collect']
            qaquestionitem['number_alsoask'] = response.meta['number_alsoask']

            if response.meta['answer_accepted'] == u'已有满意答案':
                qaquestionitem['answer_accepted'] = 'yes'
            elif response.meta['answer_accepted'] == u'暂无满意答案':
                qaquestionitem['answer_accepted'] = 'no'
                answer_accepted = False

            qaquestionitem['time'] = re.findall(r'\d\d\d\d.\d\d.\d\d \d\d:\d\d', separator.sub(' ', ' '.join(response.xpath('//div[@class="q_operate"]//span/text()').extract())))[0]

            if response.xpath('//div[@class="questions_detail_con"]/dl/dd/p/text()'):
                qaquestionitem['content'] = response.xpath('//div[@class="questions_detail_con"]/dl/dd/p/text()').extract()[0]
            else:
                qaquestionitem['content'] = ''

            qaquestionitem['content_xml'] = response.xpath('//div[@class="questions_detail_con"]/dl/dd').extract()[0]

            yield qaquestionitem

            if response.xpath('//div[@class="questions_detail_con"]//pre'):
                codeitem = CodeItem()
                codeitem['codeID'] = qaquestionitem['userID'] + qaquestionitem['qaquestionID']
                codeitem['userID'] = qaquestionitem['userID']
                codeitem['link'] = qaquestionitem['link']
                codeitem['language'] = ''
                codeitem['code'] = re.split(r'</code>', re.split(r'<code>', response.xpath('//div[@class="questions_detail_con"]//pre/code').extract()[0])[1])[0]

                yield codeitem

            if answer_accepted:
                qaansweritem = QAanswerItem()
                qaansweritem['qaanswerID'] = response.xpath('//div[@class="\n      answer_accept\n      "]/@id').extract()[0].split('_')[-1]
                qaansweritem['userID'] = response.xpath('//div[@class="\n      answer_accept\n      "]//a[@class="user_name"]/text()').extract()[0]

                dbcheck = DB_mysql()
                if dbcheck.check(qaansweritem['userID']):
                    authorItem = AuthorItem()
                    authorItem['userID'] = qaansweritem['userID']
                    authorItem['link'] = 'http://my.csdn.net/' + qaansweritem['userID']
                    authorItem['blog_crawl'] = 0
                    authorItem['user_crawl'] = 0
                    yield authorItem

                qaansweritem['link'] = response.url
                qaansweritem['answertoID'] = askerID
                qaansweritem['number_ding'] = int(
                    response.xpath('//div[@class="\n      answer_accept\n      "]//a[@class="praise"]/label/text()').extract()[0])
                qaansweritem['number_cai'] = int(
                    response.xpath('//div[@class="\n      answer_accept\n      "]//a[@class="stamp"]/label/text()').extract()[0])
                qaansweritem['number_comment'] = int(re.sub(r'\D', "", response.xpath(
                    '//div[@class="\n      answer_accept\n      "]//a[@class="collection"]/text()').extract()[0]))
                qaansweritem['best_answer'] = 'yes'
                qaansweritem['time'] = \
                response.xpath('//div[@class="\n      answer_accept\n      "]//span[@class="adopt_time"]/text()').extract()[0]
                if response.xpath('//div[@class="\n      answer_accept\n      "]/div[1]/p'):
                    qaansweritem['content'] = separator.sub(' ', ''.join(response.xpath('//div[@class="\n      answer_accept\n      "]/div[1]/p/text()').extract()))
                else:
                    qaansweritem['content'] = ''
                qaansweritem['content_xml'] = response.xpath('//div[@class="\n      answer_accept\n      "]/div[1]').extract()[0]

                yield qaansweritem

                if response.xpath('//div[@class="\n      answer_accept\n      "]//pre'):
                    codeitem = CodeItem()
                    codeitem['codeID'] = qaansweritem['userID'] + qaansweritem['qaanswerID']
                    codeitem['userID'] = qaansweritem['userID']
                    codeitem['link'] = qaansweritem['link']
                    codeitem['language'] = ''
                    codeitem['code'] = ''.join(response.xpath('//div[@class="\n      answer_accept\n      "]//pre/code/text()').extract()[0])

                    yield codeitem

        for answer in response.xpath('//div[@class="\n      answer_detail_con\n      "]'):
            qaansweritem = QAanswerItem()
            qaansweritem['qaanswerID'] = answer.xpath('@id').extract()[0].split('_')[-1]
            qaansweritem['userID'] = answer.xpath('descendant::a[@class="user_name"]/text()').extract()[0]

            if dbcheck.check(qaansweritem['userID']):
                authorItem = AuthorItem()
                authorItem['userID'] = qaansweritem['userID']
                authorItem['link'] = 'http://my.csdn.net/' + qaansweritem['userID']
                authorItem['blog_crawl'] = 0
                authorItem['user_crawl'] = 0
                yield authorItem

            qaansweritem['link'] = response.url
            qaansweritem['answertoID'] = askerID
            qaansweritem['number_ding'] = int(
                answer.xpath('descendant::a[@class="praise"]/label/text()').extract()[0])
            qaansweritem['number_cai'] = int(
                answer.xpath('descendant::a[@class="stamp"]/label/text()').extract()[0])
            qaansweritem['number_comment'] = int(re.sub(r'\D', "", answer.xpath(
                'descendant::a[@class="collection"]/text()').extract()[0]))
            qaansweritem['best_answer'] = 'no'
            qaansweritem['time'] = answer.xpath('descendant::span[@class="adopt_time"]/text()').extract()[0]
            if answer.xpath('div[1]/p'):
                qaansweritem['content'] = separator.sub(' ', ''.join(
                    answer.xpath('div[1]/p/text()').extract()))
            else:
                qaansweritem['content'] = ''
            qaansweritem['content_xml'] = answer.xpath('div[1]').extract()[0]

            yield qaansweritem

            if answer.xpath('descendant::pre').extract():
                codeitem = CodeItem()
                codeitem['codeID'] = qaansweritem['userID'] + qaansweritem['qaanswerID']
                codeitem['userID'] = qaansweritem['userID']
                codeitem['link'] = qaansweritem['link']
                codeitem['language'] = ''
                codeitem['code'] = ''.join(answer.xpath('descendant::pre/code/text()').extract())

                yield codeitem

        if response.xpath('//a[@rel="next"]'):
            nextpage_url = 'http://ask.csdn.net' + response.xpath('//a[@rel="next"]/@href').extract()[0]
            print nextpage_url
            yield Request(nextpage_url, callback=self.parse_question)







