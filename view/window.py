#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: LetsChat服务端UI
# Author: Afeng
# Date: 2019/11/24

from module.process import *


class UI(object):
    def __init__(self, title, version, width, height):
        self.width = width
        self.height = height
        self.title = title
        self.version = version
        self.mymessage_color = 'green'
        self.tag = 'my_message'

        self.window = Tk()
        self.WIDTH = self.window.winfo_screenwidth()
        self.HEIGHT = self.window.winfo_screenheight()
        self.frm_l = Frame(self.window)  # 左窗口
        self.frm_r = Frame(self.window)  # 右窗口
        self.text_history = Text(self.frm_l, width=65)  # 消息展示框
        self.input = Entry(self.frm_l, width=60)  # 信息键入框
        self.button_send = Button(self.frm_l, text='发送')  # 发送按钮
        self.button_mng = Button(self.frm_r, text='进群管理', font='Helvetica 11 bold')  # 进群申请管理按钮
        self.list_persons = Listbox(self.frm_r, height=18)  # 成员列表
        self.menu = Menu(self.frm_r, tearoff=0)  # 双击菜单

        self.process_sql = SQLProcess()
        self.process_udp = UDPProcess(self.text_history)
        self.ip = self.process_udp.ip
        self.users = self.process_udp.users

    def show(self):
        # 主窗口配置
        WIDTH = self.window.winfo_screenwidth()
        HEIGHT = self.window.winfo_screenheight()
        self.window.title(self.title + self.version)
        self.window.resizable(0, 0)
        self.window.geometry('{}x{}+{}+{}'.format(self.width, self.height,
                                                  (WIDTH - self.width) // 2, (HEIGHT - self.height) // 2))

        self.frm_l.pack(side='left')
        # 消息展示框设置
        scrol = Scrollbar(self.frm_l)
        scrol.pack(side='right', fill=Y)
        self.text_history.config(state=DISABLED, yscrollcommand=scrol.set)
        self.text_history.pack()
        scrol.config(command=self.text_history.yview)
        # 输入框设置
        self.input.bind('<Return>', self.submit)
        self.input.pack(side='left', padx=15)
        # 进群管理按钮设置
        self.button_mng.config(command=self.mng)
        self.button_mng.pack(side='left')
        # 发送按钮设置
        self.button_send.config(command=self.send_message)
        self.button_send.pack(side='right')

        self.frm_r.pack(side='right')
        # 成员列表设置
        label = Label(self.frm_r, text="成员列表")
        label.pack()
        sb = Scrollbar(self.frm_r)
        sb.pack(side='right', fill=Y)
        for i in range(20):
            self.list_persons.insert(END, str(i) + '-JoJo')
        self.list_persons.config(yscrollcommand=sb.set)
        self.list_persons.bind('<Double-Button-1>', self.do_popup)
        self.list_persons.pack(padx=5)
        sb.config(command=self.list_persons.yview)
        # 双击菜单设置
        self.menu.add_command(label='item', state=DISABLED)
        self.menu.add_separator()
        self.menu.add_command(label='私聊')
        self.menu.add_command(label='查看信息')

        self.window.mainloop()

    # TODO: 更新成员状态
    def update_users_status(self):
        pass

    # 发送消息并展示
    def send_message(self):
        var = self.input.get().strip(' ')
        if var:
            self.text_history.config(state=NORMAL)
            self.text_history.tag_config(self.tag, foreground=self.mymessage_color)
            self.text_history.insert('end', get_time() + '  我(' + self.ip + ')：\n    '
                                     + var + '\n', self.tag)
            self.text_history.config(state=DISABLED)
            self.text_history.see(END)
            self.input.delete(0, 'end')

            self.process_udp.send(var)

    def mng(self):
        logging.info("进群管理")
        width = 350
        height = 500
        window_mng = Toplevel(self.window)
        window_mng.title("进群管理")
        window_mng.resizable(0, 0)
        window_mng.geometry('{}x{}+{}+{}'.format(width, height,
                                                 (self.WIDTH - width) // 2, (self.HEIGHT - height) // 2))

        def agree():
            for n in checkeds:
                if n.get():
                    index = checkeds.index(n)
                    logging.info('同意[' + results[index][0] + ']' + results[index][1] + '进群')
                    self.process_sql.join_done(results[index][0], True)
                    checkbtns[index].destroy()

        def disagree():
            for m in checkeds:
                if m.get():
                    index = checkeds.index(m)
                    logging.info('拒绝[' + results[index][0] + ']' + results[index][1] + '进群')
                    self.process_sql.join_done(results[index][0], False)
                    checkbtns[index].destroy()

        button_agress = Button(window_mng, text='同意', fg='green', font='Fixdsys 11 bold', width=10, command=agree)
        button_disagress = Button(window_mng, text='拒绝', fg='red', font='Fixdsys 11 bold', width=10, command=disagree)

        results = self.process_sql.join_scan()
        checkbtns = []
        checkeds = []
        for i in results:
            id, nick, status, time = i[0], i[1], i[2], i[3]
            check = IntVar()
            checkeds.append(check)
            checkbtn = Checkbutton(window_mng, variable=check,
                                   text='[' + str(time) + ']' + nick + '申请进群',
                                   font='Fixdsys 10 bold', pady=20)
            checkbtns.append(checkbtn)
            checkbtn.pack()
        button_agress.pack()
        button_disagress.pack()

    # 回车发送消息
    def submit(self, e):
        self.send_message()

    # 弹出菜单
    def do_popup(self, event):
        self.menu.entryconfigure(0, label=self.list_persons.get(self.list_persons.curselection()))
        self.menu.tk_popup(event.x_root, event.y_root + 20, 0)


if __name__ == '__main__':
    UI('LetsChat_S ', 'V0.1-local', 750, 410).show()
