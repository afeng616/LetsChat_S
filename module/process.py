#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: 服务端进程操作（使用多线程）
# Author: Afeng
# Date: 2019/11/24

import time
import pymysql
import _thread
import logging
from module.utils import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class UDPProcess(object):
    def __init__(self, text_history):
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

        self.users = {}  # 用户表-供消息转发使用
        self.users_alive = {}  # 用户心跳
        self.text_history = text_history
        self.ip = ''
        self.port = 12306
        self.addr = (self.ip, self.port)  # 用于地址暂存
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.recv_send()  # 接收转发
        self.alive()  # 存活校验

    # 发送消息
    def send_data(self, message):
        for user in self.users:
            self.socket.sendto(message.encode('utf-8'), user)
        logging.info('send: [' + message + '] to clients')

    def send(self, message):
        _thread.start_new_thread(self.send_data, (message,))

    # 接收并转发消息
    def recv_send_data(self):
        while True:
            message, addr = self.socket.recvfrom(1024)
            if not addr in self.users:
                logging.info('用户' + str(addr) + '上线')
                # 告知其他客户端更新用户状态
                for client in self.users:
                    if client != addr:
                        self.socket.sendto(bytes('#[update]' + str(addr), encoding='utf-8'), client)
                logging.info('用户状态更新')
            self.users.update({addr: True})  # 更新用户状态集合
            self.addr = addr  # 更新接收端地址及端口
            message = str(message.decode('utf-8')).strip(' ')
            if message == '#[update]':
                # 更新心跳
                self.users_alive.update({addr: time.time()})
                logging.info(addr + '更新心跳')
            elif message == '#[join]':
                # TODO: 数据库操作-群表中插入数据
                logging.info(addr + '申请进群')
            else:
                self.update_message(message)
                logging.info('get: [' + message + '] from ' + str(addr))

                # 服务端向其他客户端转发消息
                for user in self.users:
                    if user != self.addr and self.users[user]:
                        self.socket.sendto(message.encode('utf-8'), tuple(user))
                    logging.info('transmit message success')

    def recv_send(self):
        _thread.start_new_thread(self.recv_send_data, ())

    def is_alive(self):
        while True:
            time.sleep(5)  # 粗略的循环定时器
            u = ()
            for user in self.users_alive:
                if time.time() - self.users_alive[user] > 10:
                    self.users[user] = False  # 更新用户状态
                    u = user
                    logging.info('用户' + str(user) + '离线')
                    # 告知其他客户端更新用户状态
                    for client in self.users:
                        if client != user:
                            self.socket.sendto(bytes('#[update]' + str(user), encoding='utf-8'), client)
                    logging.info('用户状态更新')
            if u:
                self.users_alive.pop(u)  # 字典在被循环时无法进行删除
                self.users.pop(u)  # 转发列表中删除

    def alive(self):
        _thread.start_new_thread(self.is_alive, ())

    # 更新消息展示框UI
    def update_message(self, message):
        self.text_history.config(state=NORMAL)
        self.text_history.insert('end', get_time() + ' Others（' + self.addr[0] + '）：\n    '
                                 + message + '\n')
        self.text_history.config(state=DISABLED)


class SQLProcess(object):
    def __init__(self):
        self.db = pymysql.connect('localhost', 'root', '145200')
        self.cursor = self.db.cursor()

    # 进群申请（已在客户端完成）
    def join_apply(self):
        pass

    # 进群申请查看
    def join_scan(self):
        sql = "select * from db_test.tb_groupmember where status=False"
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()

    # 进群申请处理
    def join_done(self, account, status):
        sql = ""
        if status:
            sql = "update db_test.tb_groupmember set status=True where id='%s'" % account
        else:
            sql = "delete from db_test.tb_groupmember where id='%s'" % account
        self.cursor.execute(sql)
        self.db.commit()
