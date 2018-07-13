# -*- coding: utf-8 -*-

from scrapy import Item, Field


class UserItem(Item):
    userID = Field()
    link = Field()
    nickname = Field()
    detail = Field()
    sign = Field()
    scores_label = Field()
    number_focus = Field()
    number_befoucs = Field()
    focus_userID = Field()
    befocus_userID = Field()


class AuthorItem(Item):
    userID = Field()
    link = Field()
    blog_crawl = Field()
    user_crawl = Field()


class BlogItem(Item):
    blogID = Field()
    userID = Field()
    link = Field()
    title = Field()
    time = Field()
    number_read = Field()
    number_comment = Field()
    number_ding = Field()
    number_cai = Field()
    article_type = Field()
    category = Field()
    content = Field()
    content_xml = Field()


class BlogCommentItem(Item):
    blogcommentID = Field()
    userID = Field()
    link = Field()
    commenttoID = Field()
    blogID = Field()
    authorID = Field()
    time = Field()
    content = Field()


class CodeItem(Item):
    codeID = Field()
    userID = Field()
    link = Field()
    language = Field()
    code = Field()


class BBSTopicItem(Item):
    bbstopicID = Field()
    name = Field()
    link = Field()
    category = Field()


class BBSPostItem(Item):
    bbspostID = Field()
    userID = Field()
    link = Field()
    title = Field()
    tag = Field()
    point = Field()
    number_reply = Field()
    number_ding = Field()
    number_cai = Field()
    time = Field()
    update_time = Field()
    content = Field()
    content_xml = Field()


class BBSReplyItem(Item):
    bbsreplyID = Field()
    userID = Field()
    link = Field()
    replytoID = Field()
    score = Field()
    number_ding = Field()
    number_cai = Field()
    time = Field()
    content = Field()
    content_xml = Field()


class QAquestionItem(Item):
    qaquestionID = Field()
    userID = Field()
    link = Field()
    title = Field()
    tag = Field()
    point = Field()
    number_answer = Field()
    number_read = Field()
    number_collect = Field()
    number_alsoask = Field()
    answer_accepted = Field()
    time = Field()
    content = Field()
    content_xml = Field()


class QAanswerItem(Item):
    qaanswerID = Field()
    userID = Field()
    link = Field()
    answertoID = Field()
    number_ding = Field()
    number_cai = Field()
    number_comment = Field()
    best_answer = Field()
    time = Field()
    content = Field()
    content_xml = Field()