#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 22:46
# @Author  : youfeng
# @Site    : 
# @File    : server.py
# @Software: PyCharm
import queue
import threading

from config import ACCOUNT_LIST
from grab_order import GrabOrder
from logger import Logger

log = Logger('wangzhuan.log').get_logger()


def run(grab_obj):
    grab_obj.run()


def main():
    q = queue.Queue()
    thread_list = []
    for user_info_dict in ACCOUNT_LIST:
        # 判断是否开启账户
        if user_info_dict.get("start"):
            t = threading.Thread(target=run, args=(GrabOrder(user_info_dict, log, q),))

            thread_list.append(t)

    # 启动多线程
    for t in thread_list:
        t.start()

    # 阻塞抢单
    for t in thread_list:
        t.join()


if __name__ == '__main__':
    main()
