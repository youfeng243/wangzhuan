#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 22:46
# @Author  : youfeng
# @Site    : 
# @File    : server.py
# @Software: PyCharm
import os

from alipay_model import AliPayModel
from checkout_order import CheckoutOrder
from common.mysql import MySQL
from grab_api import GrabAPI
from grab_thread import GrabThread
from logger import Logger

log = Logger('wangzhuan.log').get_logger()

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "wangzhuan",
    "log": log
}

sql_obj = MySQL(**db_config)


def get_grab_list(alipay_account):
    sql = "select username, password, token, cookie from user_info where start = 1"
    result_list = sql_obj.find_all(sql)

    if not isinstance(result_list, tuple) or len(result_list) <= 0:
        log.error("没有设置蓝海账户，无法抢单")
        os._exit(0)

    grab_list = []
    for item in result_list:
        grab_obj = GrabAPI(item[0], item[1], item[3], alipay_account, item[2], log)
        grab_list.append(grab_obj)

    return grab_list


def update_qr_code(grab_list, alipay_account):
    pic_path = "./picture/" + alipay_account + '.jpeg'
    if not os.path.exists(pic_path):
        log.error("当前账户没有配置二维码，不进行抢单: alipay_account = {}".format(alipay_account))
        os._exit(0)

    for grab_obj in grab_list:
        open_list = grab_obj.request_qr_list()
        result = grab_obj.update_config_all(pic_path, open_list)
        if not result:
            log.error("部分账户更新二维码失败: user_id = {}", grab_obj.get_user_id())
            os._exit(0)


def main():
    grab_thread_list = []

    # 先校验上一次的订单是否为空单
    CheckoutOrder(sql_obj, log)

    # 再获取到最优的支付宝账户
    alipay_account = AliPayModel(sql_obj, log).get_best_account()

    # 初始化所有的抢单账户信息
    grab_list = get_grab_list(alipay_account)

    # 这里上传最新账号支付宝二维码到海蓝账户
    update_qr_code(grab_list, alipay_account)

    # 运行抢单线程池
    for grab_obj in grab_list:
        grab_thread = GrabThread(sql_obj, grab_obj, log)
        grab_thread_list.append(grab_thread)

    # 阻塞等待线程结束
    for grab_thread in grab_thread_list:
        grab_thread.join()


if __name__ == '__main__':
    main()
