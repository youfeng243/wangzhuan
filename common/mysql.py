#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-03-14 12:25
# @Author  : youfeng
# @Site    : 
# @File    : mysql.py
# @Software: PyCharm
import pymysql

from logger import Logger


class MySQL(object):
    def __init__(self, host="localhost", port=3306,
                 user=None, password=None,
                 database=None, log=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.log = log

        self.db = pymysql.connect(host=self.host,
                                  port=self.port,
                                  user=self.user,
                                  password=self.password,
                                  database=self.database)
        # 显示版本信息
        self.__show_version()

    def __del__(self):
        self.db.close()

    def __show_version(self):
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = self.db.cursor()

        # 使用 execute()  方法执行 SQL 查询
        cursor.execute("SELECT VERSION()")

        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchone()
        cursor.close()

        self.log.info("Database version : {}".format(data[0]))

    def insert_batch(self, sql, data_list):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        try:
            # 执行sql语句
            cursor.executemany(sql, data_list)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db.rollback()
            self.log.error("插入数据失败: sql = {} data = {}", sql, data_list)
            self.log.exception(e)

        # 关闭游标
        cursor.close()

    def insert(self, sql, data):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        try:
            # 执行sql语句
            cursor.execute(sql, data)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db.rollback()
            self.log.error("插入数据失败: sql = {} data = {}", sql, data)
            self.log.exception(e)

        # 关闭游标
        cursor.close()

    def delete_all(self, sql):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db.rollback()
            self.log.error("删除数据失败: sql = {}", sql)
            self.log.exception(e)

        # 关闭游标
        cursor.close()

    def execute(self, sql):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            # 如果发生错误则回滚
            self.db.rollback()
            self.log.error("删除数据失败: sql = {}", sql)
            self.log.exception(e)

        # 关闭游标
        cursor.close()

    def count(self, sql):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            result = cursor.fetchone()[0]
        except Exception as e:
            # 如果发生错误则回滚
            self.db.rollback()
            self.log.error("删除数据失败: sql = {}", sql)
            self.log.exception(e)
            result = -1

        # 关闭游标
        cursor.close()
        return result

    def find_all(self, sql):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results

    def find_one(self, sql):
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = self.db.cursor()
        try:
            # 使用 execute()  方法执行 SQL 查询
            cursor.execute(sql)

            # 使用 fetchone() 方法获取单条数据.
            data = cursor.fetchone()
            return data
        except Exception as e:
            self.log.error("获取数据失败: sql = {}".format(sql))
            self.log.exception(e)
        finally:
            cursor.close()

        return None


def main():
    log = Logger('mysql.log').get_logger()
    db_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "database": "wangzhuan",
        "log": log
    }

    mysql = MySQL(**db_config)

    def __is_order_exist(order_id):
        sql = """select * from order_info where `order_id` = {}""".format(order_id)
        result = mysql.find_one(sql)
        if result is not None:
            return True

        return False

    __is_order_exist(213031111128)


if __name__ == '__main__':
    main()
