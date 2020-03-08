#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-03-08 22:09
# @Author  : youfeng
# @Site    : 
# @File    : order_print.py
# @Software: PyCharm
import os


class OrderPrint(object):
    def __init__(self, sql_obj, log):
        self.__sql_obj = sql_obj
        self.log = log

        # 获取所有的订单信息
        self.__order_list = self.__get_current_order_list()

        # 获取所有的支付宝账号信息
        self.__pay_dict = self.__get_pay_account_dict()

        # 打印对应账号的转账情况
        self.__print_summary()

    def __get_current_order_list(self):
        sql = 'select alipay_account, money from order_info where is_invalid = 0 and checkout = 1 and to_days(create_time)=to_days(now())'

        result_list = self.__sql_obj.find_all(sql)
        if not isinstance(result_list, tuple):
            self.log.error("获取订单数据失败")
            os._exit(0)

        return result_list

    def __get_pay_account_dict(self):
        sql = '''select account, max_times, max_money from alipay_account_info where start = 1'''
        result_list = self.__sql_obj.find_all(sql)
        if not isinstance(result_list, tuple):
            self.log.error("获取支付宝账户失败...")
            os._exit(0)

        if len(result_list) <= 0:
            self.log.error("当前没有有效的支付宝账户")
            os._exit(0)

        result_dict = {}
        for item in result_list:
            result_dict[item[0]] = {
                "account": item[0],
                "max_times": item[1],
                "money": item[2]
            }

        return result_dict

    def __print_summary(self):

        if len(self.__order_list) <= 0:
            self.log.info("###########还未开张,暂未盈利!###########")
            return

        total_times = 0
        total_money = 0

        account_dict = {}

        for order in self.__order_list:
            account = order[0]
            money = order[1]

            if account in account_dict:
                account_dict[account].append(money)
            else:
                account_dict[account] = [money]

            total_times += 1
            total_money += money

        self.log.info("###########当前转账总额度: {}".format(total_money))
        self.log.info("###########当前转账总次数: {}".format(total_times))
        self.log.info("###########当前盈利总额度: {}".format(total_money * 0.009))

        self.log.info("###########各账号转账盈利情况统计###########")
        for account, money_list in account_dict.items():

            ac_item = self.__pay_dict.get(account)
            max_times = 0
            max_money = 0
            if isinstance(ac_item, dict):
                max_times = ac_item.get("max_times")
                max_money = ac_item.get("money")

            self.log.info("#################################")
            self.log.info("###########当前统计账号: {}".format(account))
            self.log.info("###########当前转账总额: {}".format(sum(money_list)))
            self.log.info("###########最大转账总额: {}".format(max_money))
            self.log.info("###########当前转账次数: {}".format(len(money_list)))
            self.log.info("###########最大转账次数: {}".format(max_times))
            self.log.info("#################################")
