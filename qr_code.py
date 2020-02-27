#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 20:27
# @Author  : youfeng
# @Site    : 
# @File    : qr_code.py
# @Software: PyCharm
import zxing


def decode_qr_code(code_img_path):
    reader = zxing.BarCodeReader()
    barcode = reader.decode(code_img_path)
    return barcode.parsed


if __name__ == '__main__':
    print(decode_qr_code('./picture/WechatIMG463.jpeg'))
    print(decode_qr_code('./picture/13532369240.jpeg'))
    print(decode_qr_code('./picture/WechatIMG464.jpeg'))
