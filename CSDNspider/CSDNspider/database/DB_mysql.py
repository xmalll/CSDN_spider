# -*- coding: utf-8 -*-
import MySQLdb
from scrapy.utils.project import get_project_settings


class DB_mysql():
    def __init__(self):
        self.settings = get_project_settings()
        self.host = self.settings['MYSQL_HOST']
        self.port = self.settings['MYSQL_PORT']
        self.user = self.settings['MYSQL_USER']
        self.passwd = self.settings['MYSQL_PASSWD']
        self.db = self.settings['MYSQL_DBNAME']

    def query(self, sql):
        conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        cur = conn.cursor()

        cur.execute(sql)
        query_result = cur.fetchall()

        cur.close()
        conn.close()

        return query_result

    def check(self, user):
        conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        cur = conn.cursor()

        sql = 'select * from author where userID = "' + user + '"'
        cur.execute(sql)
        check_result = cur.fetchall()

        cur.close()
        conn.close()

        if check_result:
            return False
        else:
            return True

    def update(self, user, option):
        conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db, charset='utf8')
        cur = conn.cursor()

        if option == 1:
            sql = 'update author set blog_crawl = 1 where userID = "' + user + '"'
        elif option == 2:
            sql = 'update author set user_crawl = 1 where userID = "' + user + '"'
        cur.execute(sql)
        conn.commit()

        cur.close()
        conn.close()





