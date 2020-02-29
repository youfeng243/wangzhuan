#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-26 20:27
# @Author  : youfeng
# @Site    : 
# @File    : qr_code.py
# @Software: PyCharm
import zxing
import base64
import qrcode


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


def save_qr_code(url, pic_path):
    # 调用qrcode的make()方法传入url或者想要展示的内容
    img = qrcode.make(url)
    # 写入文件
    with open(pic_path, 'wb') as f:
        img.save(f)


if __name__ == '__main__':
    # save_qr_code("https://qr.alipay.com/fkx11018z9gypgjao0wwm19?t=1582883541195", "1111.jpg")

    # print(decode_qr_code('./picture/WechatIMG463.jpeg'))
    print(decode_qr_code('./picture/13302963506.jpg'))
    # print(decode_qr_code('./save/13302963506.jpg'))
    # print(get_pic_base64("./picture/13532369240.jpeg"))
