#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-29 23:15
# @Author  : youfeng
# @Site    : 
# @File    : alipay_model.py
# @Software: PyCharm
import os


class AliPayModel(object):
    '''
    获取当前适合的支付宝账户
    '''

    # 每个支付宝一天内最多接20单
    MAX_ORDER_NUM = 20

    # 每个支付宝接单额度 8000
    MAX_ORDER_MONEY = 8000

    # 支付宝最大额度
    MAX_PAY_MONEY = 20000

    def __init__(self, sql_obj, log):
        self.log = log
        self.__sql_obj = sql_obj

        self.__account_dict = self.__get_account()

        # 获取当天所有与当前支付宝相关的订单信息
        self.__order_dict = self.__get_order()

        # 获取到最优的支付宝账户
        self.__best_account = self.__cal_best_account(self.__order_dict)

    def get_best_account(self):
        return self.__best_account

    def score(self, total, num):
        return total + num * 100

    def __cal_best_account(self, order_dict):
        '''
        计算出最佳账户信息
        :param order_dict:
        :return:
        '''
        best_account = None
        min_order_num = 99999
        min_money = 200000

        for account, order_list in order_dict.items():
            order_num = len(order_list)
            total_money = sum(order_list)

            order_score = self.score(total_money, order_num)
            min_score = self.score(min_money, min_order_num)

            if min_score > order_score:
                best_account = account
                min_money = total_money
                min_order_num = order_num
                continue

            if min_score < order_score:
                continue

            if min_order_num > order_num:
                best_account = account
                min_money = total_money
                min_order_num = order_num
                continue

        if best_account is None:
            self.log.info("当前所有账户都超出额度，停止抢单！！！！")
            os._exit(0)

        self.log.info("当前最佳账号: account = {} score = {} money = {} num = {}".format(
            best_account, self.score(min_money, min_order_num), min_money, min_order_num
        ))
        return best_account

    def __is_yesterday_limit(self, account, max_money):
        sql = """SELECT sum(money) FROM order_info WHERE  alipay_account = '{}' and TO_DAYS(NOW()) - TO_DAYS(create_time) = 1 and checkout = 1 and is_invalid = 0""".format(
            account)

        result = self.__sql_obj.find_one(sql)
        if result is None:
            return False

        if result[0] >= max_money:
            return True

        return False

    def __is_yesterday_max(self):
        sql = """SELECT alipay_account, money FROM order_info WHERE TO_DAYS(NOW()) - TO_DAYS(create_time) = 1 and checkout = 1 and is_invalid = 0"""
        result_list = self.__sql_obj.find_all(sql)
        if result_list is None or len(result_list) <= 0:
            return None

        max_money = -1
        max_account = None

        account_dict = {}
        for item in result_list:
            account = item[0]
            money = item[1]

            if account in account_dict:
                account_dict[account] += money
            else:
                account_dict[account] = money

            if max_money < account_dict[account]:
                max_money = account_dict[account]
                max_account = account

        return max_account

    def __get_order(self):
        sql = 'select alipay_account, money from order_info where is_invalid = 0 and checkout = 1 and to_days(create_time)=to_days(now())'

        result_list = self.__sql_obj.find_all(sql)
        if not isinstance(result_list, tuple):
            self.log.error("获取订单数据失败")
            os._exit(0)

        temp_dict = {}

        # 先初始化订单信息
        for account, ac_item in self.__account_dict.items():
            temp_dict[account] = []

        for item in result_list:
            account = item[0]
            money = item[1]

            if account not in temp_dict:
                continue

            temp_dict[account].append(money)

        # 获得昨日转账最大的账户
        yesterday_max_account = self.__is_yesterday_max()

        result_dict = {}
        for account, money_list in temp_dict.items():
            ac_item = self.__account_dict.get(account)
            max_times = ac_item.get("max_times")
            max_money = ac_item.get("max_money")

            if self.__is_yesterday_limit(account, max_money) or yesterday_max_account == account:
                max_times -= 1
                self.log.info("当前账号昨日超额或转账最多，限制次数减一: account = {} max_times = {}".format(
                    account, max_times))

            if len(money_list) >= max_times or sum(money_list) >= max_money:
                self.log.info(
                    "当前支付账号超出限制: account = {} max_times = {} max_money = {} cur_times = {} cur_money = {}".format(
                        account, max_times, max_money, len(money_list), sum(money_list)))
                continue

            result_dict[account] = money_list

        return result_dict

    def __get_account(self):
        '''
        获取所有的支付宝账户信息
        :return:
        '''
        sql = '''select account, max_times, max_money from alipay_account_info where start = 1'''
        result_list = self.__sql_obj.find_all(sql)
        if not isinstance(result_list, tuple):
            self.log.error("获取支付宝账户失败...")
            os._exit(0)

        if len(result_list) <= 0:
            self.log.error("当前没有有效的支付宝账户")
            os._exit(0)

        account_dict = {}
        for item in result_list:
            account_dict[item[0]] = {
                "account": item[0],
                "max_times": item[1],
                "max_money": item[2]
            }

        return account_dict
