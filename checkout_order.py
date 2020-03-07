#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-29 21:50
# @Author  : youfeng
# @Site    : 
# @File    : checkout_order.py
# @Software: PyCharm
import os
import time

import requests

from common import date_util
from user_info_api import UserInfoAPI


class CheckoutOrder(object):
    SUCCESS = 2
    FAIL = 3
    '''
    校验订单是否为空单
    '''

    def __init__(self, sql_obj, log):
        self.__sql_obj = sql_obj
        self.log = log
        # 缓存失败的订单
        self.__fail_order_dict = {}

        # 获取成功订单
        self.__success_order_dict = {}

        self.__user_dict = self.__get_user_dict()

        # 校验订单是否为空单
        self.__check_order()

    def __get_user_dict(self):

        user_list = UserInfoAPI(self.__sql_obj, self.log).get_all_user_list()

        user_dict = {}
        for user in user_list:
            user_dict[user.get("username")] = user

        return user_dict

    def __request_order_list(self, token, cookie, pay_type):
        '''
        获取远程账户列表
        :return:
        '''
        url = 'http://h52h.5188wangzhuan.com/api/v2.0/OrderList?version=2.0'

        headers = {
            'Host': 'h52h.5188wangzhuan.com',
            'Connection': 'keep-alive',
            'Content-Length': '232',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'http://h52h.5188wangzhuan.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/24.0)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://h52h.5188wangzhuan.com/index.html?v=2.32',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Cookie': cookie,
            'X-Requested-With': 'io.dcloud.W2Axx.lh',
        }

        post_data = {
            "token": token,
            "startTime": date_util.get_cur_date('%Y/%m/%d'),
            "endTime": date_util.get_any_date(-30, format='%Y/%m/%d'),
            "PayType": pay_type,
            "p": 1,
        }

        for _ in range(3):
            try:
                resp = requests.post(url=url, headers=headers, data=post_data)
                if resp is None:
                    self.log.error("当前请求站点异常，退出流程:")
                    time.sleep(1)
                    continue

                if resp.status_code != 200:
                    self.log.error("请求站点状态码异常: url = {} code = {}".format(
                        url, resp.status_code))
                    time.sleep(1)
                    continue

                self.log.info("日志: {} {}".format(url, resp.text))

                json_data = resp.json()
                if json_data is None:
                    self.log.error("返回数据包异常: url = {} json_data = None".format(url))
                    os._exit(0)

                code = json_data.get("code")
                if code != 0:
                    self.log.error("请求返回code异常: url = {} data = {}".format(url, resp.text))
                    os._exit(0)

                result_list = json_data.get("result")
                if not isinstance(result_list, list):
                    self.log.error("获取失败订单列表异常: url = {} data = {}".format(url, resp.text))
                    os._exit(0)

                return result_list

            except Exception as e:
                self.log.error("请求判断订单信息异常")
                self.log.exception(e)
                time.sleep(1)
        self.log.error("请求失败订单信息失败")
        os._exit(0)

    def __check_by_manual(self, order):
        self.log.info("========当前需要校验的订单信息========")
        self.log.info("回款ID: order_id = {}".format(order[1]))
        self.log.info("会员ID: user_id = {}".format(order[2]))
        self.log.info("到款支付宝账户: alipay = {}".format(order[3]))
        self.log.info("到款金额: money = {}".format(order[4]))
        self.log.info("如已到款直接回车，未到款则输入1:")
        answer = input()
        # 如果是空单 则需要更新订单信息
        if answer == '1':
            sql = 'update order_info set checkout = 1, is_invalid = 1 where id = {}'.format(order[0])
            self.__sql_obj.execute(sql)
        else:
            sql = 'update order_info set checkout = 1 where id = {}'.format(order[0])
            self.__sql_obj.execute(sql)

    def __get_fail_order_list(self, user_dict):
        if user_dict is None:
            return None

        username = user_dict.get("username")
        if username is None:
            self.log.error("当前账户信息不存在: user_dict = {}".format(user_dict))
            return None

        if username in self.__fail_order_dict:
            self.log.info("从缓存中获取失败订单信息: username = {}".format(username))
            return self.__fail_order_dict.get(username)

        fail_order_list = self.__request_order_list(user_dict.get("token"), user_dict.get("cookie"), self.FAIL)
        if not isinstance(fail_order_list, list):
            self.log.error("请求失败订单信息失败: username = {}".format(username))
            return None

        self.__fail_order_dict[username] = fail_order_list
        return fail_order_list

    def __get_success_order_list(self, user_dict):
        if user_dict is None:
            return None

        username = user_dict.get("username")
        if username is None:
            self.log.error("当前账户信息不存在: user_dict = {}".format(user_dict))
            return None

        if username in self.__success_order_dict:
            self.log.info("从缓存中获取成功订单信息: username = {}".format(username))
            return self.__success_order_dict.get(username)

        order_list = self.__request_order_list(user_dict.get("token"), user_dict.get("cookie"), self.SUCCESS)
        if not isinstance(order_list, list):
            self.log.error("请求成功订单信息失败: username = {}".format(username))
            return None

        self.__success_order_dict[username] = order_list
        return order_list

    def __is_fail_order(self, order, user_dict):
        # 获取服务端的失败订单列表
        fail_order_list = self.__get_fail_order_list(user_dict)
        if not isinstance(fail_order_list, list):
            return None

        for item in fail_order_list:
            order_id = item.get("OrderID")
            if str(order_id) == str(order[1]):
                return True
        return None

    def __is_success_order(self, order, user_dict):
        # 获取服务端的失败订单列表
        success_order_list = self.__get_success_order_list(user_dict)
        if not isinstance(success_order_list, list):
            return None

        for item in success_order_list:
            order_id = item.get("OrderID")
            if str(order_id) == str(order[1]):
                return True
        return None

    def __check_from_server(self, order, user_dict):

        if user_dict is None:
            self.__check_by_manual(order)
            return

        # 如果是失败订单
        if self.__is_fail_order(order, user_dict):
            sql = 'update order_info set checkout = 1, is_invalid = 1 where id = {}'.format(order[0])
            self.__sql_obj.execute(sql)
            self.log.info("当前订单是空单，自动化确认: user_id = {} order_id = {}".format(order[2], order[1]))
            return

        # 如果是成功订单
        if self.__is_success_order(order, user_dict):
            sql = 'update order_info set checkout = 1 where id = {}'.format(order[0])
            self.__sql_obj.execute(sql)
            self.log.info("当前订单是成功订单，自动化确认: user_id = {} order_id = {}".format(order[2], order[1]))
            return

        # 手动确认
        self.__check_by_manual(order)

    def __check_order(self):
        '''
        获取所有未校验的订单
        :return:
        '''
        sql = '''select id, order_id, user_id, alipay_account, money, username from order_info where checkout = 0'''
        order_list = self.__sql_obj.find_all(sql)

        if len(order_list) <= 0:
            self.log.info("当前没有需要校验的订单信息...")
            return

        for order in order_list:
            self.__check_from_server(order, self.__user_dict.get(order[5]))

        # 清空缓存
        self.__fail_order_dict = {}
        self.__success_order_dict = {}
