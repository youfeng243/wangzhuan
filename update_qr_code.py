#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-27 14:08
# @Author  : youfeng
# @Site    : 
# @File    : update_qr_code.py
# @Software: PyCharm
import threading

from config import ACCOUNT_LIST
from grab_order import GrabOrder
from logger import Logger

log = Logger('update_qr_code.log').get_logger()


def main():
    for user_info_dict in ACCOUNT_LIST:
        # 判断是否开启账户
        if user_info_dict.get("start"):
            GrabOrder(user_info_dict, log)


if __name__ == '__main__':
    main()
