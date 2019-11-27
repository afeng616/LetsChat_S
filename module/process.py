#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 服务端进程操作（使用多线程）
# Author: Afeng
# Date: 2019/11/24

import _thread
import logging
from module.utils import *


class Process(object):
    def __init__(self, text_history):
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

        self.users = set()
        self.text_history = text_history
        self.ip = ''
        self.port = 12306
        self.addr = (self.ip, self.port)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.recv_send()

    # 发送消息
    def send_data(self, message):
        self.socket.sendto(message.encode('utf-8'), self.addr)
        logging.info('send：' + message + ' to ' + str(self.addr))

    def send(self, message):
        _thread.start_new_thread(self.send_data, (message,))

    # 接收并转发消息
    def recv_send_data(self):
        while True:
            message, addr = self.socket.recvfrom(1024)
            self.users.add(addr)  # 更新用户集合
            self.addr = addr  # 更新接收端地址及端口
            message = str(message.decode('utf-8')).strip(' ')
            if message != '':
                self.update_message(message)

            logging.info('from ' + str(addr) + ' get: ' + message)
            # TODO: 转发给其他客户端
            for user in self.users:
                if user != self.addr:
                    self.socket.sendto(message.encode('utf-8'), tuple(user))
                logging.info('transmit message success')

    def recv_send(self):
        _thread.start_new_thread(self.recv_send_data, ())

    # 更新消息展示框UI
    def update_message(self, message):
        self.text_history.config(state=NORMAL)
        self.text_history.insert('end', get_time() + ' Others（' + self.addr[0] + '）：\n    '
                                 + message + '\n')
        self.text_history.config(state=DISABLED)
