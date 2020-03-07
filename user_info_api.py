#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-03-05 20:34
# @Author  : youfeng
# @Site    : 
# @File    : user_info_api.py
# @Software: PyCharm
import os


class UserInfoAPI(object):
    def __init__(self, sql_obj, log):
        self.log = log
        self.__sql_obj = sql_obj

    def get_user_list(self):
        sql = "select username, password, token, cookie from user_info where start = 1"
        result_list = self.__sql_obj.find_all(sql)

        if not isinstance(result_list, tuple) or len(result_list) <= 0:
            self.log.error("没有设置蓝海账户，无法抢单")
            os._exit(0)

        user_list = []
        for item in result_list:
            user_list.append({"username": item[0],
                              "password": item[1],
                              "token": item[2],
                              "cookie": item[3]
                              })

        return user_list

    def get_all_user_list(self):
        sql = "select username, password, token, cookie from user_info"
        result_list = self.__sql_obj.find_all(sql)

        if not isinstance(result_list, tuple) or len(result_list) <= 0:
            self.log.error("没有设置蓝海账户，无法抢单")
            os._exit(0)

        user_list = []
        for item in result_list:
            user_list.append({"username": item[0],
                              "password": item[1],
                              "token": item[2],
                              "cookie": item[3]
                              })

        return user_list
