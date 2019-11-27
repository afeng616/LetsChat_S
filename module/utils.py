#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 服务端工具模块
# Author: Afeng
# Date: 2019/11/24

import datetime as d
from tkinter import *
from socket import *


# 获取本机本地ip
def get_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


# 获取当前时间
def get_time():
    return d.datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
