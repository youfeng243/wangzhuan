#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 22:46
# @Author  : youfeng
# @Site    : 
# @File    : server.py
# @Software: PyCharm
import os
import signal
import time

from alipay_model import AliPayModel
from checkout_order import CheckoutOrder
from common import date_util
from common.mysql import MySQL
from grab_api import GrabAPI
from grab_thread import GrabThread
from logger import Logger
from qr_code import decode_qr_code
from user_info_api import UserInfoAPI

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

is_running = True


def process_quit(signo, frame):
    global is_running
    log.info('收到信号退出进程...')
    is_running = False


def get_grab_list(user_info_list, alipay_account):
    grab_list = []
    for item in user_info_list:
        grab_obj = GrabAPI(item.get("username"), item.get("password"), item.get("cookie"), alipay_account,
                           item.get("token"), log)
        grab_list.append(grab_obj)

    return grab_list


# 存储二维码信息
def save_qr_code(pic_path, alipay_account):
    full_url = decode_qr_code(pic_path)
    if full_url is None:
        log.error("二维码识别失败: pic_path = {}".format(pic_path))
        os._exit(0)

    url = full_url.split("?t=")[0]
    log.info("当前需要校验的链接: full_url = {} url = {}".format(full_url, url))

    # 获取到当天所有的二维码信息
    sql = 'select `account`, `url` from alipay_account_record where `account` = "{}" and to_days(`create_time`)=to_days(now())'.format(
        alipay_account)

    result_list = sql_obj.find_all(sql)
    if isinstance(result_list, tuple):
        for item in result_list:
            item_url = item[1].split("?t=")[0]
            if url == item_url:
                log.info("当前需要存储的链接已经存在于数据库: full_url = {}".format(full_url))
                return

    # 开始存储链接
    sql = """INSERT INTO `alipay_account_record` (`account`, `url`, `create_time`)
            VALUES (%s,%s,%s)"""

    insert_list = [(alipay_account,
                    full_url,
                    date_util.get_now_time())]

    sql_obj.insert_batch(sql, insert_list)


def update_qr_code(grab_list, alipay_account):
    pic_path = "./picture/" + alipay_account + '.jpeg'
    if not os.path.exists(pic_path):
        log.error("当前账户没有配置二维码，不进行抢单: alipay_account = {}".format(alipay_account))
        os._exit(0)

    # 这里存储当前二维码信息
    save_qr_code(pic_path, alipay_account)

    for grab_obj in grab_list:
        open_list = grab_obj.request_qr_list()
        result = grab_obj.update_index_config(pic_path, open_list[0])
        if not result:
            log.error("部分账户更新二维码失败: user_id = {}", grab_obj.get_user_id())
            os._exit(0)


def main():
    signal.signal(signal.SIGINT, process_quit)
    signal.signal(signal.SIGTERM, process_quit)
    signal.signal(signal.SIGQUIT, process_quit)
    signal.signal(signal.SIGUSR1, process_quit)

    grab_thread_list = []

    user_info_list = UserInfoAPI(sql_obj, log).get_user_list()

    # 先校验上一次的订单是否为空单
    CheckoutOrder(sql_obj, log)

    # 再获取到最优的支付宝账户
    alipay_account = AliPayModel(sql_obj, log).get_best_account()

    # 初始化所有的抢单账户信息
    grab_list = get_grab_list(user_info_list, alipay_account)

    # 这里上传最新账号支付宝二维码到海蓝账户
    update_qr_code(grab_list, alipay_account)

    # 运行抢单线程池
    for grab_obj in grab_list:
        grab_thread = GrabThread(sql_obj, grab_obj, log)
        grab_thread_list.append(grab_thread)

    global is_running
    while is_running:
        is_run = False
        for grab_thread in grab_thread_list:
            if grab_thread.is_alive():
                is_run = True
                break

        if not is_run:
            break

        time.sleep(2)

    for grab_thread in grab_thread_list:
        grab_thread.force_stop()

    # 阻塞等待线程结束
    for grab_thread in grab_thread_list:
        grab_thread.join()

    # 结束时需要检测是否有

    log.info("安全退出进程!!!")


if __name__ == '__main__':
    main()
