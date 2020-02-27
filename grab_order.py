#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 22:31
# @Author  : youfeng
# @Site    : 
# @File    : grab_order.py
# @Software: PyCharm
import copy
import json
import os
import time

import requests

from qr_code import decode_qr_code


class GrabOrder(object):
    def __init__(self, user_info_dict, log):
        self.log = log
        self.__user_info = user_info_dict
        self.__username = self.__user_info.get("username")
        self.__password = self.__user_info.get("password")
        self.__token = self.__user_info.get("token")
        self.__session = self.__get_session(self.__username,
                                            self.__password,
                                            self.__token)
        self.__alipay_pic = self.__user_info.get("alipay")
        self.__alipay_pic_path = self.__get_pic_path(self.__alipay_pic)
        self.__alipay_url = self.__get_alipay_url(self.__alipay_pic_path)

        self.__phone = self.__user_info.get("alipay").split(".")[0]
        self.log.info("当前账户支付宝对应手机号码: {}".format(self.__phone))
        self.__cookie = self.__user_info.get("cookie")

        # 获取收款码列表
        self.__open_index = 0
        self.__open_list = self.get_qr_list()
        self.__open_length = len(self.__open_list)
        self.log.info("当前收款账号数目: length = {}".format(self.__open_length))

    def __get_pic_path(self, pic_name):
        system = self.__get_system_info()
        if system == 'win':
            pic_path = '.\\picture\\' + pic_name
        else:
            pic_path = "./picture/" + pic_name

        return pic_path

    # 获得系统版本信息
    def __get_system_info(self):
        import platform
        system = platform.system()
        if system == 'Darwin':
            return 'mac'
        if system == 'Linux':
            return 'linux'
        return 'win'

    def __get_alipay_url(self, pic_path):
        url = decode_qr_code(pic_path)
        self.log.info("当前解析到支付宝链接: url = {}".format(url))
        return url

    def __get_session(self, username, password, token):
        '''
        获取session
        :param username:
        :param password:
        :param token:
        :return:
        '''
        url = 'http://h52h.5188wangzhuan.com/api/v2.0/Login?version=2.0'
        headers = {
            'Host': 'h52h.5188wangzhuan.com',
            'Connection': 'keep-alive',
            'Content-Length': '234',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'http://h52h.5188wangzhuan.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; COL-AL10 Build/HUAWEICOL-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.132 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/35.294117)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'io.dcloud.W2Axx.lh',
            'Referer': 'http://h52h.5188wangzhuan.com/index.html?v=2.3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        post_data = {
            'account': username,
            'password': password,
            "token": token,
        }

        session = requests.session()
        try:
            resp = session.post(url=url, headers=headers, data=post_data)
            if resp is None:
                self.log.error("当前请求站点异常，退出流程")
                os._exit(0)

            if resp.status_code != 200:
                self.log.error("请求站点状态码异常: url = {} code = {}".format(
                    url, resp.status_code))
                os._exit(0)

            self.log.info("日志: {} {}".format(url, resp.text))

            json_data = resp.json()
            if json_data is None:
                self.log.error("返回数据包异常: url = {} json_data = None".format(url))
                os._exit(0)

            code = json_data.get("code")
            if code != 0:
                self.log.error("请求返回code异常: url = {} data = {}".format(url, resp.text))
                os._exit(0)

            # 这里解析到 userID account
            user = json_data.get("user")
            if not isinstance(user, dict):
                self.log.error("解析用户信息失败: url = {} data = {}".format(url, resp.text))
                os._exit(0)

            self.__user_id = user.get("userid")
            self.__account = user.get("user_email")

            return session
        except Exception as e:
            self.log.error("请求登录异常，退出流程")
            self.log.exception(e)
            os._exit(0)

    # 判断是否有订单 listenOrder 如有 则退出
    def __have_order(self):
        url = 'http://h52h.5188wangzhuan.com/api/v2.0/ListenOrder?version=2.0'

        headers = {
            "Host": "h52h.5188wangzhuan.com",
            "Connection": "keep-alive",
            "Content-Length": "174",
            "Accept": "application/json, text/plain, */*",
            "Origin": "http://h52h.5188wangzhuan.com",
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/24.0)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://h52h.5188wangzhuan.com/index.html?v=2.3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,en-US;q=0.9",
            "Cookie": self.__cookie,
            "X-Requested-With": "io.dcloud.W2Axx.lh"
        }

        post_data = {
            "token": self.__token,
        }

        try:
            resp = requests.post(url=url, headers=headers, data=post_data)
            if resp is None:
                self.log.error("当前请求站点异常，退出流程: {}".format(self.__user_id))
                os._exit(0)

            if resp.status_code != 200:
                self.log.error("请求站点状态码异常: {} url = {} code = {}".format(
                    self.__user_id, url, resp.status_code))
                os._exit(0)

            self.log.info("日志: {} {} {}".format(self.__user_id, url, resp.text))

            json_data = resp.json()
            if json_data is None:
                self.log.error("返回数据包异常: {} url = {} json_data = None".format(self.__user_id, url))
                os._exit(0)

            code = json_data.get("code")
            if code != 0:
                self.log.error("请求返回code异常: {} url = {} data = {}".format(self.__user_id, url, resp.text))
                os._exit(0)

            result = json_data.get('result')
            if not isinstance(result, list):
                self.log.error("当前result数据格式不正确: {} url = {} data = {}".format(self.__user_id, url, resp.text))
                os._exit(0)

            if len(result) > 0:
                order_dict = result[0]
                if isinstance(order_dict, dict):
                    self.log.info("###################订单信息###################")
                    self.log.info("当前订单: {} {} {}".format(self.__phone, self.__user_id, self.__account))
                    self.log.info("{}".format(json.dumps(order_dict, indent=4, ensure_ascii=False)))
                return True

            return False
        except Exception as e:
            self.log.error("请求判断订单信息异常，退出流程")
            self.log.exception(e)
            os._exit(0)

    # 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
    def __is_listen_order(self):
        url = 'http://h52h.5188wangzhuan.com/api/v2.0/getGrabData?version=2.0'

        headers = {
            "Host": "h52h.5188wangzhuan.com",
            "Connection": "keep-alive",
            "Content-Length": "174",
            "Accept": "application/json, text/plain, */*",
            "Origin": "http://h52h.5188wangzhuan.com",
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/24.0)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://h52h.5188wangzhuan.com/index.html?v=2.3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,en-US;q=0.9",
            "X-Requested-With": "io.dcloud.W2Axx.lh",
            'Cookie': self.__cookie
        }

        post_data = {
            "token": self.__token,
        }

        try:
            resp = requests.post(url=url, headers=headers, data=post_data)
            if resp is None:
                self.log.error("当前请求站点异常，退出流程: {}".format(self.__user_id))
                os._exit(0)

            if resp.status_code != 200:
                self.log.error("请求站点状态码异常: {} url = {} code = {}".format(
                    self.__user_id, url, resp.status_code))
                os._exit(0)

            self.log.info("日志: {} {} {}".format(self.__user_id, url, resp.text))

            json_data = resp.json()
            if json_data is None:
                self.log.error("返回数据包异常: {} url = {} json_data = None".format(self.__user_id, url))
                os._exit(0)

            code = json_data.get("code")
            if code != 0:
                self.log.error("请求返回code异常: {} url = {} data = {}".format(self.__user_id, url, resp.text))
                os._exit(0)

            listen = json_data.get('listen')
            if listen == 0:
                return False

            if listen == 1:
                return True

            self.log.error("当前监听状态异常: {} url = {} data = {}".format(self.__user_id, url, resp.text))
            os._exit(0)
        except Exception as e:
            self.log.error("请求判断订单信息异常，退出流程: {}".format(self.__user_id))
            self.log.exception(e)
            os._exit(0)

    # 开启抢单 休眠3s
    def __open_listen_order(self):
        url = 'http://h52h.5188wangzhuan.com/api/v2.0/openQueue?version=2.0'

        headers = {
            "Host": "h52h.5188wangzhuan.com",
            "Connection": "keep-alive",
            "Content-Length": "956",
            "Accept": "application/json, text/plain, */*",
            "Origin": "http://h52h.5188wangzhuan.com",
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/24.0)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://h52h.5188wangzhuan.com/index.html?v=2.3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,en-US;q=0.9",
            "Cookie": self.__cookie,
            "X-Requested-With": "io.dcloud.W2Axx.lh"
        }

        cnt = 0

        # 遍历所有的帐户，如果所有帐户均不可用，则需要退出抢单 并提示错误
        while cnt < self.__open_length:
            cnt += 1

            self.__open_index += 1
            self.__open_index %= self.__open_length
            self.log.info("当前使用帐户信息: {} open_index = {}".format(self.__user_id, self.__open_index))

            param_dict = copy.deepcopy(self.__open_list[self.__open_index])

            param_dict['ChannelStatus'] = 1
            param_dict['ChannelOrder'] = 0

            post_data = {
                "token": self.__token,
                'channel': json.dumps(param_dict)
            }

            try:
                resp = requests.post(url=url, headers=headers, data=post_data)
                if resp is None:
                    self.log.error("当前请求站点异常，退出流程: {}".format(self.__user_id))
                    os._exit(0)

                if resp.status_code != 200:
                    self.log.error("请求站点状态码异常: {} url = {} code = {}".format(
                        self.__user_id, url, resp.status_code))
                    os._exit(0)

                self.log.info("日志: {} {} {}".format(self.__user_id, url, resp.text))

                json_data = resp.json()
                if json_data is None:
                    self.log.error("返回数据包异常: {} url = {} json_data = None".format(self.__user_id, url))
                    os._exit(0)

                code = json_data.get("code")
                if code != 0:
                    self.log.error("当前帐户抢单异常: {} url = {} data = {} open_index = {}".format(
                        self.__user_id, url, resp.text, self.__open_index))
                    self.log.info("本次抢单失败，切换账号: {} open_index = {}".format(self.__user_id, self.__open_index))
                    continue

                return True
            except Exception as e:
                self.log.error("请求判断订单信息异常，退出流程: {}".format(self.__user_id))
                self.log.exception(e)
                os._exit(0)

        if cnt >= self.__open_length:
            self.log.error("当前所有帐户均不可用, 退出抢单: {} url = {}".format(self.__user_id, url))
            os._exit(0)

    def get_qr_list(self):
        '''
        获取远程账户列表
        :return:
        '''
        url = 'http://h52h.5188wangzhuan.com/api/v2.0/getQrcodeList?version=2.0'

        headers = {
            'Host': 'h52h.5188wangzhuan.com',
            'Connection': 'keep-alive',
            'Content-Length': '196',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'http://h52h.5188wangzhuan.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; COL-AL10 Build/HUAWEICOL-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.132 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/35.294117)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'io.dcloud.W2Axx.lh',
            'Referer': 'http://h52h.5188wangzhuan.com/index.html?v=2.3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': self.__cookie
        }

        post_data = {
            "token": self.__token,
        }

        try:
            resp = requests.post(url=url, headers=headers, data=post_data)
            if resp is None:
                self.log.error("当前请求站点异常，退出流程: {}".format(self.__user_id))
                os._exit(0)

            if resp.status_code != 200:
                self.log.error("请求站点状态码异常: {} url = {} code = {}".format(
                    self.__user_id, url, resp.status_code))
                os._exit(0)

            self.log.info("日志: {} {} {}".format(self.__user_id, url, resp.text))

            json_data = resp.json()
            if json_data is None:
                self.log.error("返回数据包异常: {} url = {} json_data = None".format(self.__user_id, url))
                os._exit(0)

            code = json_data.get("code")
            if code != 0:
                self.log.error("请求返回code异常: {} url = {} data = {}".format(self.__user_id, url, resp.text))
                os._exit(0)

            qrcodes = json_data.get("qrcodes")
            if not isinstance(qrcodes, list):
                self.log.error("获取收款账户列表异常: {} url = {} data = {}".format(self.__user_id, url, resp.text))
                os._exit(0)

            return qrcodes

        except Exception as e:
            self.log.error("请求判断订单信息异常，退出流程: {}".format(self.__user_id))
            self.log.exception(e)
            os._exit(0)

    def upload_gathering(self):
        pass

    def run(self):
        self.log.info("开始启动抢单: {} {} {}".format(self.__phone, self.__user_id, self.__account))

        while True:
            # 判断是否有订单 listenOrder 如有 则退出
            if self.__have_order():
                self.log.info("当前存在订单，停止抢单! {} {} {}".format(self.__phone, self.__user_id, self.__account))
                os._exit(0)

            # 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
            if self.__is_listen_order():
                self.log.info("当前正在抢单,休眠2s: {} {} {}".format(self.__phone, self.__user_id, self.__account))
                time.sleep(2)
                continue

            # 开启抢单 休眠3s
            if self.__open_listen_order():
                self.log.info("开启抢单，休眠20秒: {} {} {}".format(self.__phone, self.__user_id, self.__account))
                time.sleep(20)


if __name__ == '__main__':
    from logger import Logger

    log = Logger('wangzhuan_test.log').get_logger()
    from config import ACCOUNT_LIST

    grab = GrabOrder(ACCOUNT_LIST[1], log)

    log.info(grab.get_qr_list())
