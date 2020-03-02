#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-03-02 10:46
# @Author  : youfeng
# @Site    : 
# @File    : mail.py
# @Software: PyCharm

import json
import smtplib
from email.mime.text import MIMEText

from common.configer import Configer


def send_email(mail_host, mail_user, mail_pass, sender, receivers, content, title):
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    email_client = None
    try:
        email_client = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        email_client.login(mail_user, mail_pass)  # 登录验证
        email_client.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)
    finally:
        if email_client is not None:
            email_client.quit()


def send_mail_by_file(file_path, content_dict, title):
    conf_dict = Configer(file_path).get_mail_dict()
    send_mail_by_config(conf_dict, content_dict, title)


def send_mail_by_config(conf_dict, content_dict, title):
    mail_host = conf_dict.get("mail_host")
    mail_user = conf_dict.get("mail_user")
    mail_pass = conf_dict.get("mail_pass")
    sender = conf_dict.get("sender")
    receiver = conf_dict.get("receiver")
    receiver_list = receiver.split(",")
    content = json.dumps(content_dict, ensure_ascii=False, indent=4)

    send_email(mail_host, mail_user, mail_pass, sender, receiver_list, content, title)


def main():
    send_mail_by_file("../mail.ini", {"蓝海订单邮件提醒测试": "蓝海订单邮件提醒测试"}, "这是蓝海订单测试邮件")


if __name__ == '__main__':
    main()
