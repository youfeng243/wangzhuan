#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 20:27
# @Author  : youfeng
# @Site    : 
# @File    : qr_code.py
# @Software: PyCharm
import zxing
import base64


def decode_qr_code(code_img_path):
    reader = zxing.BarCodeReader()
    barcode = reader.decode(code_img_path)
    return barcode.parsed


def get_pic_base64(pic_path):
    '''
    只支持jepg jpg
    :param pic_path:
    :return:
    '''
    with open(pic_path, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        s = base64_data.decode()
        return 'data:image/jpeg;base64,{}'.format(s)


if __name__ == '__main__':
    # print(decode_qr_code('./picture/WechatIMG463.jpeg'))
    # print(decode_qr_code('./picture/13532369240.jpeg'))
    print(decode_qr_code('./picture/13532369240.jpeg'))
    print(get_pic_base64("./picture/13532369240.jpeg"))