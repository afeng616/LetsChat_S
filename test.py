#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 
# Author: Afeng
# Date: 2019/12/16

from module.process import *


def process_sql_test():
    r = SQLProcess().join_scan()
    for i in r:
        a, b, c = i[1], i[2], i[3]
        print(a, b, c)


if __name__ == '__main__':
    process_sql_test()
