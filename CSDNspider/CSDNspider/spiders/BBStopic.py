# -*- coding: utf-8 -*-
import scrapy

from CSDNspider.items import BBSTopicItem


class Blogspider(scrapy.Spider):
    name = 'bbs_topic_spider'
    allowed_domains = ['bbs.csdn.net']
    start_urls = ['http://bbs.csdn.net/map']

    def parse(self, response):
        count = 0
        category_list = response.xpath('//div[@class="map"]//ul')
        for category in category_list:
            category_name = category.xpath('h2/a/text()').extract()[0]
            bbstopicitem = BBSTopicItem()
            count = count + 1
            bbstopicitem['bbstopicID'] = count
            bbstopicitem['link'] = 'http://bbs.csdn.net' + category.xpath('h2/a/@href').extract()[0]
            bbstopicitem['name'] = category_name
            bbstopicitem['category'] = category_name
            yield bbstopicitem

            topic_list = category.xpath('li')
            for topic in topic_list:
                bbstopicitem = BBSTopicItem()
                count = count + 1
                bbstopicitem['bbstopicID'] = count
                bbstopicitem['link'] = 'http://bbs.csdn.net' + topic.xpath('a/@href').extract()[0]
                bbstopicitem['name'] = topic.xpath('a/text()').extract()[0]
                bbstopicitem['category'] = category_name
                #print bbstopicitem['name']
                yield bbstopicitem

