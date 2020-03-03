#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 22:46
# @Author  : youfeng
# @Site    : 
# @File    : server.py
# @Software: PyCharm
import copy
import json
import os
import random
import threading
import time

from common import date_util
from common.date_util import get_cur_time
from common.mail import send_mail_by_file
from play_audio import play_hint_audio
from qr_code import save_qr_code

is_running = True


class GrabThread(threading.Thread):
    def __init__(self, sql_obj, grab_obj, log):
        super().__init__()
        self.log = log
        self.__grab_obj = grab_obj
        self.__sql_obj = sql_obj
        self.__open_index = 0
        # 启动线程
        self.start()

    def force_stop(self):
        global is_running
        is_running = False

    def __save_order(self, order_dict):
        sql = """INSERT INTO `order_info` (`order_id`, `username`, `user_id`, `alipay_account`, `money`, `is_invalid`, `json`, `checkout`, `create_time`)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        order_id = order_dict.get("OrderID")
        username = self.__grab_obj.get_username()
        user_id = self.__grab_obj.get_user_id()
        alipay_account = self.__grab_obj.get_alipay_account()
        money = order_dict.get("OrderMoney")
        is_invalid = 0
        json_str = json.dumps(order_dict)
        checkout = 0
        create_time = get_cur_time()

        insert_list = [(order_id,
                        username,
                        user_id,
                        alipay_account,
                        money,
                        is_invalid,
                        json_str,
                        checkout, create_time)]

        self.__sql_obj.insert_batch(sql, insert_list)

        # 这里发送邮件
        send_dict = {
            "会员ID": self.__grab_obj.get_user_id(),
            "登录账号": self.__grab_obj.get_username(),
            "支付宝账号": self.__grab_obj.get_alipay_account(),
            "订单金额:": order_dict.get("OrderMoney"),
            "订单详情": order_dict
        }
        send_mail_by_file("./mail.ini", send_dict, "lanhai订单{}".format(date_util.get_now_time()))

    def __open_listen_order(self, channel_status, open_list):
        cnt = 0

        # 获取到最新二维码路径
        pic_path = self.get_new_qrcode_path(open_list)

        # 遍历所有的帐户，如果所有帐户均不可用，则需要退出抢单 并提示错误
        while cnt < len(open_list):
            cnt += 1

            self.__open_index += 1
            self.__open_index %= len(open_list)
            self.log.info("当前使用帐户信息: {} open_index = {}".format(self.__grab_obj.get_user_id(), self.__open_index))

            param_dict = copy.deepcopy(open_list[self.__open_index])

            #  先更新对应的配置
            result = self.__grab_obj.update_index_config(pic_path, param_dict)
            if result:
                # 如果更新成功， 则重新获取最新的配置信息
                open_list = self.__grab_obj.request_qr_list()
                param_dict = copy.deepcopy(open_list[self.__open_index])

            param_dict['ChannelStatus'] = channel_status
            param_dict['ChannelOrder'] = 0
            success = self.__grab_obj.open_listen_order(param_dict)
            if not success:
                continue

            return True
        if cnt >= len(open_list):
            self.log.error("当前所有帐户均不可用, 退出抢单: {}".format(self.__grab_obj.get_user_id()))
            os._exit(0)

    def __create_new_qr_code(self, param_dict, alipay_account):
        # 先获取最新的支付宝链接
        full_url = param_dict.get("AccountCode")
        url = full_url.split("?t=")[0]
        self.log.info("当前分解出来url url = {}".format(url))
        url += "?t=" + str(int(time.time() * 1000))
        self.log.info("当前合并的url为: url = {}".format(url))

        save_path = "./save/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        qr_code_path = save_path + alipay_account + "_" + str(threading.currentThread().ident) + ".jpeg"
        # 存储最新的二维码
        save_qr_code(url, qr_code_path)

        return qr_code_path

    def get_new_qrcode_path(self, open_list):
        # 获取到当前使用的支付宝信息
        alipay_account = self.__grab_obj.get_alipay_account()

        # 如果没有配置任何收款码信息 则不需要上传
        if not isinstance(open_list, list):
            return

        # 获取最新的二维码
        return self.__create_new_qr_code(open_list[0], alipay_account)

    # def __update_config(self, open_list):
    #     # 获取最新的二维码
    #     qr_code_path = self.get_new_qrcode_path(open_list)
    #
    #     # 更新配置信息
    #     self.__grab_obj.update_config_all(qr_code_path, open_list)

    def run(self):

        # # 先获取到最新的收款码信息
        open_list = self.__grab_obj.request_qr_list()

        # 如果有正在抢单 则先取消抢单
        self.__open_listen_order(0, open_list)

        global is_running
        while True:

            if not is_running:
                while True:
                    # 判断是否有订单 listenOrder 如有 则退出
                    success, order_dict = self.__grab_obj.is_have_order()
                    if success:
                        self.__save_order(order_dict)
                        break

                    # 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
                    if self.__grab_obj.is_listen_order():
                        self.log.info(
                            "收到进程退出信号，正在抢单,休眠2s: {} {}".format(self.__grab_obj.get_user_id(),
                                                               self.__grab_obj.get_alipay_account()))
                        time.sleep(2)
                        continue
                    break
                break

            # 判断是否有订单 listenOrder 如有 则退出
            success, order_dict = self.__grab_obj.is_have_order()
            if success:
                is_running = False
                self.__save_order(order_dict)
                # 这里播放语音
                play_hint_audio()
                break

            # 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
            if self.__grab_obj.is_listen_order():
                self.log.info(
                    "当前正在抢单,休眠2s: {} {}".format(self.__grab_obj.get_user_id(), self.__grab_obj.get_alipay_account()))
                time.sleep(2)
                continue

            # 获取最新收款码配置
            open_list = self.__grab_obj.request_qr_list()

            # 开启抢单 休眠3s
            if self.__open_listen_order(1, open_list):
                sleep_time = random.randint(20, 26)
                self.log.info("开启抢单，休眠{}秒: {} {}".format(sleep_time, self.__grab_obj.get_user_id(),
                                                         self.__grab_obj.get_alipay_account()))
                time.sleep(sleep_time)

        self.log.info("当前线程正常退出: {} {}".format(self.__grab_obj.get_user_id(), self.__grab_obj.get_alipay_account()))
