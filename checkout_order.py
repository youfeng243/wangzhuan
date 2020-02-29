#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-29 21:50
# @Author  : youfeng
# @Site    : 
# @File    : checkout_order.py
# @Software: PyCharm


class CheckoutOrder(object):
    '''
    校验订单是否为空单
    '''

    def __init__(self, sql_obj, log):
        self.__sql_obj = sql_obj
        self.log = log

    def check_order(self):
        '''
        获取所有未校验的订单
        :return:
        '''
        sql = '''select id, order_id, user_id, alipay_account, money from order_info where checkout = 0'''
        order_list = self.__sql_obj.find_all(sql)

        if len(order_list) <= 0:
            self.log.info("当前没有需要校验的订单信息...")
            return

        for order in order_list:
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
