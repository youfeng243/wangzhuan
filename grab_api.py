#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-29 22:20
# @Author  : youfeng
# @Site    : 
# @File    : grab_api.py
# @Software: PyCharm
import copy
import json
import os

import requests

from qr_code import get_pic_base64


class GrabAPI(object):
    def __init__(self, username, password, cookie, alipay_account, token, log):
        self.log = log
        self.__username = username
        self.__password = password
        self.__cookie = cookie
        self.__alipay_account = alipay_account
        self.__token = token

        # 获取到会员ID
        self.__user_id = self.request_user_id()

    def get_username(self):
        '''
        获取用户信息: 16860684261
        :return:
        '''
        return self.__username

    def get_user_id(self):
        '''
        获取会员ID： 19373
        :return:
        '''
        return self.__user_id

    def get_alipay_account(self):
        '''
        获取支付宝账户
        :return:
        '''
        return self.__alipay_account

    def request_user_id(self):
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
            'account': self.__username,
            'password': self.__password,
            "token": self.__token,
        }

        try:
            resp = requests.post(url=url, headers=headers, data=post_data)
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

            return user.get("userid")
        except Exception as e:
            self.log.error("请求登录异常，退出流程")
            self.log.exception(e)
            os._exit(0)

    def request_qr_list(self):
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

    def update_config(self, pic_path, open_list):
        '''
        上传配置信息
        :param pic_path:
        :param open_list:
        :return:
        '''

        # 判断图片是否存在，如果存在则上传，不存在则不上传
        if not os.path.exists(pic_path):
            self.log.info("当前二维码不存在,不更新配置: {} pic_path = {}".format(
                self.__user_id, pic_path))
            return False

        url = 'http://h52h.5188wangzhuan.com/api/v2.0/saveQrcode?version=2.0'

        headers = {
            'Host': 'h52h.5188wangzhuan.com',
            'Connection': 'keep-alive',
            'Content-Length': '13801',
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

        for param_dict in open_list:
            qrcode_dict = copy.deepcopy(param_dict)
            qrcode_dict['ChannelName'] = self.__alipay_account
            qrcode_dict['ChannelRemark'] = ""
            post_data = {
                "token": self.__token,
                "qrcode": json.dumps(qrcode_dict),
                "pass": self.__password,
                "files": get_pic_base64(pic_path)
            }

            try:
                resp = requests.post(url=url, headers=headers, data=post_data)
                if resp is None:
                    self.log.error("当前请求站点异常，退出流程: {}".format(self.__user_id))
                    os._exit(0)

                if resp.status_code != 200:
                    self.log.error("请求站点状态码异常: {} url = {} code = {}".format(
                        self.__user_id, url, resp.status_code))
                    return False

                self.log.info("日志: {} {} {}".format(self.__user_id, url, resp.text))

                json_data = resp.json()
                if json_data is None:
                    self.log.error("返回数据包异常: {} url = {} json_data = None".format(self.__user_id, url))
                    return False

                code = json_data.get("code")
                if code != 0:
                    self.log.error("请求返回code异常: {} url = {} data = {}".format(self.__user_id, url, resp.text))
                    return False

                self.log.info("图片保存结果: {} pic_path = {} result = {}".format(
                    self.__user_id, pic_path, resp.text))
            except Exception as e:
                self.log.error("请求判断订单信息异常，退出流程: {}".format(self.__user_id))
                self.log.exception(e)
                os._exit(0)
                return False
        return True

    # 开启抢单 休眠3s
    def open_listen_order(self, param):
        '''
        抢单接口
        :param param:
        :return:
        '''
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

        param_dict = copy.deepcopy(param)

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
                self.log.error("当前帐户抢单异常: {} url = {} data = {}".format(
                    self.__user_id, url, resp.text))
                self.log.info("本次抢单失败，切换账号: {}".format(self.__user_id))
                return False

            return True
        except Exception as e:
            self.log.error("请求判断订单信息异常，退出流程: {}".format(self.__user_id))
            self.log.exception(e)
            os._exit(0)

        return False

    # 判断是否有订单 listenOrder 如有 则退出
    def is_have_order(self):
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
                    self.log.info("当前订单: {} {} {}".format(self.__user_id, self.__alipay_account, self.__username))
                    self.log.info("{}".format(json.dumps(order_dict, indent=4, ensure_ascii=False)))
                return True, order_dict

            return False, None
        except Exception as e:
            self.log.error("请求判断订单信息异常，退出流程")
            self.log.exception(e)
            os._exit(0)

        return False, None

    # 判断是否正在抢单
    def is_listen_order(self):
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
