#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-03-02 11:00
# @Author  : youfeng
# @Site    : 
# @File    : configer.py
# @Software: PyCharm
import configparser


class Configer(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.con = configparser.ConfigParser()
        self.con.read(file_path, encoding='utf-8')
        self.sections = self.con.sections()

    def get_mail_dict(self):
        return dict(self.con.items("mail"))
