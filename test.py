#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 
# Author: Afeng
# Date: 2019/12/16

from module.process import *


def process_sql_test():
    r = SQLProcess().members()
    for i in r:
        print(i)


def str_test():
    str = "sss,aasdf,"
    print(str[:-1].split(','))


def if_else_test():
    s = 'aabbb'
    if s[:2] == 'aa':
        print('aa')
    elif s:
        print('bb')


def list_test():
    l = (('3117005390', 'afeng'), ('3117004494', 'jian'))
    print(l.index((3117005390, 'afeng')))


if __name__ == '__main__':
    list_test()
