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
    def __init__(self, text_history, list_persons):
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

        self.users_addr = {}  # 用户表（地址）-供消息转发使用  {'id': (addr), }
        self.users_alive = {}  # 用户心跳  {'id': time, }

        self.users_id = []  # 在线用户id表
        self.members = []  # 群用户成员  [('id', 'nickname'), ]
        self.text_history = text_history
        self.list_persons = list_persons
        self.ip = ''
        self.port = 12306
        self.addr = (self.ip, self.port)  # 用于地址暂存
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.alive()  # 存活校验
        self.process = SQLProcess()
        self.recv_send()  # 接收转发

    # 发送消息（转发）
    def send_data(self, message):
        for user in self.users_addr:
            self.socket.sendto(message.encode('utf-8'), self.users_addr[user])
        logging.info('send: [' + message + '] to clients')

    def send(self, message):
        _thread.start_new_thread(self.send_data, (message,))

    # 接收并转发消息
    def recv_send_data(self):
        while True:
            message, addr = '', ()
            try:
                message, addr = self.socket.recvfrom(1024)
            except ConnectionResetError:  # 远程主机强迫关机一个现有连接（用户离线可能触发）
                pass
            message = str(message.decode('utf-8')).strip(' ')
            flag, user_id = message[:9], message[9:]
            if message and user_id not in self.users_addr:
                self.users_id.append(user_id)
                self.update_users_status(user_id, True)
                logging.info('用户' + user_id + '上线')
                users = ''
                for user in self.users_id:
                    users = user + ','
                self.socket.sendto(bytes('#[update]' + users[:-1], encoding='utf-8'), addr)
                logging.info('向该用户发送在线用户id表')  # 首次进入，发送在线成员id表
                # 告知客户端更新用户状态
                for client in self.users_addr:
                    self.socket.sendto(bytes('#[update]' + str(addr), encoding='utf-8'), self.users_addr[client])
                logging.info('用户状态更新')
                self.users_addr.update({user_id: addr})  # 更新用户状态集合
            # self.addr = addr  # 更新接收端地址及端口
            if flag == '#[update]':
                # 更新心跳
                self.users_alive.update({user_id: time.time()})
                logging.info(user_id + '更新心跳')
            elif message:
                self.update_message(message)
                logging.info('get: [' + message + '] from ' + str(addr))

                # 服务端向其他客户端转发消息
                for user in self.users_addr:
                    if user != addr:
                        self.socket.sendto(message.encode('utf-8'), self.users_addr[user])
                    logging.info('transmit message success')

    def recv_send(self):
        _thread.start_new_thread(self.recv_send_data, ())

    def is_alive(self):
        while True:
            time.sleep(5)  # 粗略的循环定时器
            u = ()
            for user in self.users_alive:
                if time.time() - self.users_alive[user] > 3:
                    u = user
                    self.update_users_status(user, False)
                    logging.info('用户' + user + '离线')
                    # 告知客户端更新用户状态
                    for client in self.users_addr:
                        self.socket.sendto(bytes('#[update]' + str(user), encoding='utf-8'), self.users_addr[client])
                    logging.info('用户状态更新')
            if u:
                self.users_alive.pop(u)  # 字典在被循环时无法进行删除
                self.users_addr.pop(u)  # 转发列表中删除

    def alive(self):
        _thread.start_new_thread(self.is_alive, ())

    # 更新消息展示框UI
    def update_message(self, message):
        self.text_history.config(state=NORMAL)
        self.text_history.insert('end', get_time() + ' Others（' + self.addr[0] + '）：\n    '
                                 + message + '\n')
        self.text_history.config(state=DISABLED)

    # 初始化成员列表组件
    def init_users_status(self):
        # 获取群成员
        for _, i in self.members:
            self.list_persons.insert(END, str(i))
        for i, user in enumerate(self.list_persons.get(0, len(self.members))):
            # 更改用户状态
            if user in self.users_id:
                self.list_persons.itemconfig(i, fg='green')
            else:
                self.list_persons.itemconfig(i, fg='red')

    # 更新用户状态
    def update_users_status(self, user_id, status):
        nickname = self.process.nickname(user_id)
        index = self.members.index((user_id, nickname))
        self.list_persons.itemconfig(index, fg='green' if status else 'red')
        logging.info(user_id + '上线' if status else '下线')


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

    # 获取成员
    def members(self):
        sql = "select id, nickname from db_test.tb_groupmember where status=True order by nickname"
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()

    # 通过id获取昵称
    def nickname(self, id):
        sql = "select nickname from db_test.tb_groupmember where id='%s'" % id
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()[0][0]
