# coding=utf-8
'''
公共方法.
'''

import decimal
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time

# def strQ2B(ustring):
#     """全角转半角"""
#     rstring = ""
#     for uchar in ustring:
#         inside_code = ord(uchar)
#         if inside_code == 12288:  # 全角空格直接转换
#             inside_code = 32
#         elif 65281 <= inside_code <= 65374:  # 全角字符（除空格）根据关系转化
#             inside_code -= 65248
#
#         rstring += unichr(inside_code)
#     return rstring
#
#
# def strB2Q(ustring):
#     """半角转全角"""
#     rstring = ""
#     for uchar in ustring:
#         inside_code = ord(uchar)
#         if inside_code == 32:  # 半角空格直接转化
#             inside_code = 12288
#         elif 32 <= inside_code <= 126:  # 半角字符（除空格）根据关系转化
#             inside_code += 65248
#
#         rstring += unichr(inside_code)
#     return rstring

pat_ymd = re.compile(u'(\d+)')


# def format_date(beforedate):
#     str_group = re.findall(pat_ymd, beforedate if beforedate is not None else '')
#     if beforedate is not None and beforedate != '' and len(str_group) == 3:
#         yy = str(str_group[0])
#         mm = str(str_group[1])
#         dd = str(str_group[2])
#         if len(yy) < 2:
#             raise StandardError('formdate_error:' + str(str_group))
#         if len(mm) < 2:
#             mm = '0' + mm
#         if len(dd) < 2:
#             dd = '0' + dd
#         date = '{0}-{1}-{2}'.format(yy, mm, dd)
#     else:
#         date = beforedate
#     return date


def json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def get_time_stamp():
    return str(int(time.time() * 1000))


def get_cur_time():
    return time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())


def get_cur_date(fmt="%Y-%m-%d"):
    return time.strftime(fmt, time.localtime())


# 获取任意时间
def get_any_date(days, format="%Y-%m-%d"):
    import datetime
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=days)
    n_days = now + delta

    return n_days.strftime(format)


def get_change_stamp(str_time):
    return int(time.mktime(time.strptime(str_time, '%Y-%m-%d %H:%M:%S')))


def get_pid_log_name(log_name):
    return log_name + '_' + str(os.getpid()) + '.log'


def sub_time(cur_time, pre_time):
    cur_localtime = time.mktime(time.strptime(cur_time, '%Y-%m-%d %H:%M:%S'))
    pre_localtime = time.mktime(time.strptime(pre_time, '%Y-%m-%d %H:%M:%S'))
    sub_second = int(cur_localtime - pre_localtime)
    return sub_second


def get_now_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_gm_time():
    return time.strftime(u"%a %b %d %Y %H:%M:%S GMT+0800 (CST)", time.gmtime(time.time() + 8 * 60 * 60))


def get_gm_other_time():
    return time.strftime(u"%a %b %d %Y %H:%M:%S GMT 0800 (CST)", time.gmtime(time.time() + 8 * 60 * 60))


def get_random_num():
    x = [random.random()]
    decimal.getcontext().prec = 16
    return decimal.Decimal(x[0]) * 1


# 生成mongodb存储ID
def generator_id(param_dict, company, province):
    hash_key = ''
    for key, value in param_dict.iteritems():
        hash_key += str(value) + '#'
    hash_key += company + '#'
    hash_key += province + '#'
    return hashlib.sha256(hash_key).hexdigest()


# 详情页参数生成ID 方式
def generator_id_by_md5(param_dict, company, province):
    hash_key = ''
    for key, value in param_dict.iteritems():
        hash_key += str(value) + '#'
    hash_key += company + '#'
    hash_key += province + '#'

    md5_obj = hashlib.md5()
    md5_obj.update(hash_key)
    return md5_obj.hexdigest().lower()


# 获得系统版本信息
def get_system_info():
    import platform
    system = platform.system()
    if system == 'Darwin':
        return 'mac'
    if system == 'Linux':
        return 'linux'
    return 'linux'


def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = p.stdout.readline()
        if line:
            sys.stdout.flush()
        else:
            break
    p.wait()


# 生成 省份与企业联合主键md5
def gen_key_md5(company, province):
    hash_key = company + '#'
    hash_key += province + '#'

    md5_obj = hashlib.md5()
    md5_obj.update(hash_key)
    company_md5 = md5_obj.hexdigest().lower()

    return company_md5


if __name__ == '__main__':
    print(get_any_date(1))
    print(get_any_date(-5))
    print(get_any_date(-35))
