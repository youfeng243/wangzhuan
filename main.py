#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-24 10:00
# @Author  : youfeng
# @Site    : 
# @File    : main.py
# @Software: PyCharm


import time

from logger import Logger

log = Logger('wangzhuan.log').get_logger()


# 判断是否有订单 listenOrder 如有 则退出
def have_order():
    pass


# 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
def is_listen_order():
    pass


# 开启抢单 休眠3s
def open_listen_order():
    pass


def main():
    while True:
        # 判断是否有订单 listenOrder 如有 则退出
        if have_order():
            log.info("当前存在订单，不进行抢单...")
            break

        # 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
        if is_listen_order():
            log.info("当前正在抢单，休眠3秒...")
            time.sleep(3)
            continue

        # 开启抢单 休眠3s
        open_listen_order()
        log.info("开启抢单，休眠3秒...")
        time.sleep(3)


if __name__ == '__main__':
    main()
