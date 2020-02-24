#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-24 10:00
# @Author  : youfeng
# @Site    : 
# @File    : main.py
# @Software: PyCharm
import json
import os
import time

import pyautogui as pag
import requests

from logger import Logger

log = Logger('wangzhuan.log').get_logger()

cookie = 'ASP.NET_SessionId=egz0pkbgoamqpd54pcmvmvyx'
token = 'kVcJcoilMXWIvcpJV7FLONVzneaveDaphs8tAenbG3ovzC73Z8uD+pZ5eZC8H9l1FS+vsYfi9qpyjFpBZZSqQSVx8h2obf+bXJa0ZNiTdFZEE7p7bOldI80qpsvpo+0TyTP9K8+Y45yL/3utJWBq5Q=='

open_list = [
    '{"Channelid":49479,"GateID":0,"ChannelType":3,"ChanneCode":"ALIPAY","ChannelName":"李珍珍1","ChannelRate":0,"ChannelStatus":1,"ChannelOrder":0,"ChannelCardNoLength":null,"ChannelCardPassLength":null,"ChannelCardRules":null,"ChannelRemark":"8426","FileStream":null,"AliveLastTime":"/Date(1582529077340)/","ChannelUseLastTime":"/Date(-62135596800000)/","SXFType":0,"PreOrderMoney":0,"MaxSXF":0,"IsDelete":0,"Memberid":19373,"AccountCode":"HTTPS://QR.ALIPAY.COM/FKX00684VAPHYFAAV09U61?t=1582530015104","pl":0}',
    # '{"Channelid":49480,"GateID":0,"ChannelType":3,"ChanneCode":"ALIPAY","ChannelName":"李珍珍2","ChannelRate":0,"ChannelStatus":1,"ChannelOrder":0,"ChannelCardNoLength":null,"ChannelCardPassLength":null,"ChannelCardRules":null,"ChannelRemark":"3146","FileStream":null,"AliveLastTime":"/Date(1582529896913)/","ChannelUseLastTime":"/Date(-62135596800000)/","SXFType":0,"PreOrderMoney":0,"MaxSXF":0,"IsDelete":0,"Memberid":19373,"AccountCode":"https://qr.alipay.com/fkx18459sjtpb7lmwj2l793?t=1582530061899","pl":0}',
    '{"Channelid":49481,"GateID":0,"ChannelType":3,"ChanneCode":"ALIPAY","ChannelName":"游丰3","ChannelRate":0,"ChannelStatus":1,"ChannelOrder":0,"ChannelCardNoLength":null,"ChannelCardPassLength":null,"ChannelCardRules":null,"ChannelRemark":"3506","FileStream":null,"AliveLastTime":"/Date(1582528365067)/","ChannelUseLastTime":"/Date(-62135596800000)/","SXFType":0,"PreOrderMoney":0,"MaxSXF":0,"IsDelete":0,"Memberid":19373,"AccountCode":"HTTPS://QR.ALIPAY.COM/FKX05314IKKOIDA3QNG8F7?t=1582529061618","pl":0}'
]
open_index = 0


# 判断是否有订单 listenOrder 如有 则退出
def have_order():
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
        "Cookie": cookie,
        "X-Requested-With": "io.dcloud.W2Axx.lh"
    }

    post_data = {
        "token": token,
    }

    try:
        resp = requests.post(url=url, headers=headers, data=post_data)
        if resp is None:
            log.error("当前请求站点异常，退出流程")
            os._exit(0)

        if resp.status_code != 200:
            log.error("请求站点状态码异常: url = {} code = {}".format(
                url, resp.status_code))
            os._exit(0)

        log.info("当前请求日志: url = {} data = {}".format(url, resp.text))

        json_data = resp.json()
        if json_data is None:
            log.error("返回数据包异常: url = {} json_data = None".format(url))
            os._exit(0)

        code = json_data.get("code")
        if code != 0:
            log.error("请求返回code异常: url = {} data = {}".format(url, resp.text))
            os._exit(0)

        result = json_data.get('result')
        if not isinstance(result, list):
            log.error("当前result数据格式不正确: url = {} data = {}".format(url, resp.text))
            os._exit(0)

        if len(result) > 0:
            order_dict = result[0]
            if isinstance(order_dict, dict):
                log.info("###################订单信息###################")
                log.info("{}".format(json.dumps(order_dict, indent=4, ensure_ascii=False)))
            return True

        return False
    except Exception as e:
        log.error("请求判断订单信息异常，退出流程")
        log.exception(e)
        os._exit(0)


# 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
def is_listen_order():
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
        "Cookie": cookie,
        "X-Requested-With": "io.dcloud.W2Axx.lh"
    }

    post_data = {
        "token": token,
    }

    try:
        resp = requests.post(url=url, headers=headers, data=post_data)
        if resp is None:
            log.error("当前请求站点异常，退出流程")
            os._exit(0)

        if resp.status_code != 200:
            log.error("请求站点状态码异常: url = {} code = {}".format(
                url, resp.status_code))
            os._exit(0)

        log.info("当前请求日志: url = {} data = {}".format(url, resp.text))

        json_data = resp.json()
        if json_data is None:
            log.error("返回数据包异常: url = {} json_data = None".format(url))
            os._exit(0)

        code = json_data.get("code")
        if code != 0:
            log.error("请求返回code异常: url = {} data = {}".format(url, resp.text))
            os._exit(0)

        listen = json_data.get('listen')
        if listen == 0:
            return False

        if listen == 1:
            return True

        log.error("当前监听状态异常: url = {} data = {}".format(url, resp.text))
        os._exit(0)
    except Exception as e:
        log.error("请求判断订单信息异常，退出流程")
        log.exception(e)
        os._exit(0)


# 开启抢单 休眠3s
def open_listen_order():
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
        "Cookie": cookie,
        "X-Requested-With": "io.dcloud.W2Axx.lh"
    }
    global open_index
    open_index += 1
    open_index %= len(open_list)
    log.info("当前使用帐户信息: open_index = {}".format(open_index))

    param = open_list[open_index]
    param_dict = json.loads(param)

    param_dict['AliveLastTime'] = "/Date({})/".format(int(time.time() * 1000))

    post_data = {
        "token": token,
        'channel': json.dumps(param_dict)
    }

    try:
        resp = requests.post(url=url, headers=headers, data=post_data)
        if resp is None:
            log.error("当前请求站点异常，退出流程")
            os._exit(0)

        if resp.status_code != 200:
            log.error("请求站点状态码异常: url = {} code = {}".format(
                url, resp.status_code))
            os._exit(0)

        log.info("当前请求日志: url = {} data = {}".format(url, resp.text))

        json_data = resp.json()
        if json_data is None:
            log.error("返回数据包异常: url = {} json_data = None".format(url))
            os._exit(0)

        code = json_data.get("code")
        if code != 0:
            log.error("当前帐户抢单异常: url = {} data = {} open_index = {}".format(
                url, resp.text, open_index))
            return False

        return True
    except Exception as e:
        log.error("请求判断订单信息异常，退出流程")
        log.exception(e)
        os._exit(0)


# 防止锁屏
def stop_lock_screen():
    pag.press("esc")


def main():
    while True:
        # 判断是否有订单 listenOrder 如有 则退出
        if have_order():
            log.info("当前存在订单，停止抢单!!!!!")
            break

        # 判断是否正在抢单， 如有 则休眠3s 重新判断是否有订单
        if is_listen_order():
            log.info("当前正在抢单，休眠2秒...")
            time.sleep(2)
            continue

        # 开启抢单 休眠3s
        if open_listen_order() == True:
            log.info("开启抢单，休眠2秒...")
            stop_lock_screen()
            time.sleep(2)
        else:
            log.info("本次抢单失败，切换账号...")


if __name__ == '__main__':
    main()
