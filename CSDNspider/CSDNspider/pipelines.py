# -*- coding: utf-8 -*-
import copy

import pymongo
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from scrapy.conf import settings

from CSDNspider.items import BBSTopicItem, UserItem, BlogItem, BlogCommentItem, CodeItem, AuthorItem, QAquestionItem, \
    QAanswerItem, BBSPostItem, BBSReplyItem


class CsdnspiderPipeline(object):
    def __init__(self, dbpool):
        client = pymongo.MongoClient(host=settings['MONGODB_HOST'], port=settings['MONGODB_PORT'])
        self.db = client[settings['MONGODB_DBNAME']]
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        asynItem = copy.deepcopy(item)
        if isinstance(item, UserItem):
            user_item = self.dbpool.runInteraction(self._UserItem_insert, item)
            user_item.addErrback(self._handle_error, asynItem, spider)
            return user_item
        elif isinstance(item, AuthorItem):
            author_item = self.dbpool.runInteraction(self._AuthorItem_insert, item)
            author_item.addErrback(self._handle_error, asynItem, spider)
            return author_item
        elif isinstance(item, BlogItem):
            blog_item = self.dbpool.runInteraction(self._BlogItem_insert, item)
            blog_item.addErrback(self._handle_error, asynItem, spider)
            return blog_item
        elif isinstance(item, BlogCommentItem):
            blogcomment_item = self.dbpool.runInteraction(self._BlogCommentItem_insert, item)
            blogcomment_item.addErrback(self._handle_error, asynItem, spider)
            return blogcomment_item
        elif isinstance(item, CodeItem):
            code_item = self.dbpool.runInteraction(self._CodeItem_insert, item)
            code_item.addErrback(self._handle_error, asynItem, spider)
            return code_item
        elif isinstance(item, BBSTopicItem):
            bbstopic_item = self.dbpool.runInteraction(self._BBSTopicItem_insert, item)
            bbstopic_item.addErrback(self._handle_error, asynItem, spider)
            return bbstopic_item
        elif isinstance(item, BBSPostItem):
            bbspost_item = self.dbpool.runInteraction(self._BBSPostItem_insert, item)
            bbspost_item.addErrback(self._handle_error, asynItem, spider)
            return bbspost_item
        elif isinstance(item, BBSReplyItem):
            bbsreply_item = self.dbpool.runInteraction(self._BBSReplyItem_insert, item)
            bbsreply_item.addErrback(self._handle_error, asynItem, spider)
            return bbsreply_item
        elif isinstance(item, QAquestionItem):
            qaquestion_item = self.dbpool.runInteraction(self._QAQuestionItem_insert, item)
            qaquestion_item.addErrback(self._handle_error, asynItem, spider)
            return qaquestion_item
        elif isinstance(item, QAanswerItem):
            qaanswer_item = self.dbpool.runInteraction(self._QAAnswerItem_insert, item)
            qaanswer_item.addErrback(self._handle_error, asynItem, spider)
            return qaanswer_item
        else:
            print 'Not Standard Item'

    def _UserItem_insert(self, conn, item):
        sql = 'insert into user (userID, link, nickname, detail, sign, number_focus, number_befoucs, focus_userID, befocus_userID) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['userID'], item['link'], item['nickname'], item['detail'], item['sign'], item['number_focus'], item['number_befoucs'], item['focus_userID'], item['befocus_userID'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['User']
        self.collection.insert(postItem)

    def _AuthorItem_insert(self, conn, item):
        sql = 'insert into author (userID, link, blog_crawl ,user_crawl) values(%s, %s, %s, %s)'
        values_params = (item['userID'], item['link'], item['blog_crawl'], item['user_crawl'])
        conn.execute(sql, values_params)

    def _BlogItem_insert(self, conn, item):
        sql = 'insert into blog (blogID, userID, link, title, time, number_read, number_comment, number_ding, number_cai, article_type, category) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['blogID'], item['userID'], item['link'], item['title'], item['time'], item['number_read'], item['number_comment'], item['number_ding'], item['number_cai'], item['article_type'], item['category'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['Blog']
        self.collection.insert(postItem)

    def _BlogCommentItem_insert(self, conn, item):
        sql = 'insert into blog_comment (blogcommentID, userID, link, commenttoID, blogID, authorID, time) values(%s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['blogcommentID'], item['userID'], item['link'], item['commenttoID'], item['blogID'], item['authorID'], item['time'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['Blog_Comment']
        self.collection.insert(postItem)

    def _BBSTopicItem_insert(self, conn, item):
        sql = 'insert into bbs_topic (bbstopicID, name, link, category) values(%s, %s, %s, %s)'
        values_params = (item['bbstopicID'], item['name'], item['link'], item['category'])
        conn.execute(sql, values_params)

    def _BBSPostItem_insert(self, conn, item):
        sql = 'insert into bbs_post (bbspostID, userID, link, title, tag, point, number_reply, number_ding, number_cai, time, update_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['bbspostID'], item['userID'], item['link'], item['title'], item['tag'], item['point'], item['number_reply'], item['number_ding'], item['number_cai'], item['time'], item['update_time'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['BBS_Post']
        self.collection.insert(postItem)

    def _BBSReplyItem_insert(self, conn, item):
        sql = 'insert into bbs_reply (bbsreplyID, userID, link, replytoID, score ,number_ding, number_cai, time) values(%s, %s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['bbsreplyID'], item['userID'], item['link'], item['replytoID'], item['score'], item['number_ding'], item['number_cai'], item['time'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['BBS_Reply']
        self.collection.insert(postItem)

    def _QAQuestionItem_insert(self, conn, item):
        sql = 'insert into qa_question (qaquestionID, userID, link, title, tag, point, number_answer, number_read, number_collect, number_alsoask, answer_accepted, time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['qaquestionID'], item['userID'], item['link'], item['title'], item['tag'], item['point'], item['number_answer'], item['number_read'], item['number_collect'], item['number_alsoask'], item['answer_accepted'], item['time'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['QA_Question']
        self.collection.insert(postItem)

    def _QAAnswerItem_insert(self, conn, item):
        sql = 'insert into qa_answer (qaanswerID, userID, link, answertoID, number_ding, number_cai, number_comment, best_answer, time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values_params = (item['qaanswerID'], item['userID'], item['link'], item['answertoID'], item['number_ding'], item['number_cai'], item['number_comment'], item['best_answer'], item['time'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['QA_Answer']
        self.collection.insert(postItem)

    def _CodeItem_insert(self, conn, item):
        sql = 'insert into code (codeID, userID, link, language) values(%s, %s, %s, %s)'
        values_params = (item['codeID'], item['userID'], item['link'], item['language'])
        conn.execute(sql, values_params)
        postItem = dict(item)
        self.collection = self.db['Code_Blog']
        self.collection.insert(postItem)

    def _handle_error(self, failure, item, spider):
        print failure
