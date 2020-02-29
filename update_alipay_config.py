#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-29 22:12
# @Author  : youfeng
# @Site    : 
# @File    : update_alipay_config.py
# @Software: PyCharm
import random
import threading
import time

from qr_code import save_qr_code


class UpdateAliPayConfig(threading.Thread):
    '''
    后台自动更新二维码线程
    '''

    def __init__(self, grab_list, log):
        super().__init__()
        self.log = log

        # 抢单API列表
        self.__grab_list = grab_list

        # 启动线程
        self.start()

        # 创建最新的二维码

    def __create_new_qr_code(self, param_dict, alipay_account):
        # 先获取最新的支付宝链接
        full_url = param_dict.get("AccountCode")
        url = full_url.split("?t=")[0]
        self.log.info("当前分解出来url url = {}".format(url))
        url += "?t=" + str(int(time.time() * 1000))
        self.log.info("当前合并的url为: url = {}".format(url))

        qr_code_path = "./save/" + alipay_account + "_" + str(threading.currentThread().ident) + ".jpg"
        # 存储最新的二维码
        save_qr_code(url, qr_code_path)

        return qr_code_path

    def run(self):
        while True:
            # 获取到最新的收款码信息
            for grab_item in self.__grab_list:
                open_list = grab_item.request_qr_list()

                # 获取到当前使用的支付宝信息
                alipay_account = grab_item.get_alipay_account()

                # 如果没有配置任何收款码信息 则不需要上传
                if not isinstance(open_list, list):
                    continue

                # 获取最新的二维码
                qr_code_path = self.__create_new_qr_code(open_list[0], alipay_account)

                # 更新配置信息
                grab_item.update_config(qr_code_path, open_list)

            sleep_time = random.randint(50, 60)
            self.log.info("当前配置更新线程休眠时间: time = {}".format(sleep_time))
            time.sleep(sleep_time)
