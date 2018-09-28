'''
name:
data:
email:
modules:python 
discribe:电子词典客户端
function:连接服务器，发出请求，接受服务端的反馈
        在这里单词的查阅是通过文本查阅方式反馈给客户端的
        a,import 模块
        b main()
            连接网络连接,从命令行直接输入
            创建套接字,尝试进行网络连接
            连接成功，进入一级界面
'''
from socket import *
import sys
import time
import getpass

# 创建网络连接
def main():
    #　文件服务器地址
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)

    #　创建套接字,　尝试进行网络连接
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print(e)
        return
    #连接成功，进入一级界面,尝试输入命令，进行一级操作
    while True:
        print("========== welcome ===========")
        print("********** 1.注册 ************")
        print("*********  2.登录 ************")
        print("********** 3.退出 ************")
        print("==============================")
        try:
            cmd = int(input("请输入命令>>"))

        except Exception as e:
            print("命令错误!!!")
            continue  # 输入格式错误的话返回一级界面继续输入
        if cmd not in [1, 2, 3]:
            print("请输入正确选项")
            sys.stdin.flush()  # 清除标准输入
            continue
        elif cmd == 1:  # 注册
            r = do_register(sockfd)
            if r == 0:
                print("注册成功")
                # login(sockfd,name)
            elif r == 1:
                print("用户存在")
            else:
                print("注册失败")

        elif cmd == 2:  # 登录
            name = do_login(sockfd)
            if name:  # 有搜索到名字的的话，登陆成功，显示二级界面
                print("登录成功")
                login(sockfd, name)
            else:
                print("用户名和密码不正确")
        elif cmd == 3:  # 退出
            sockfd.send(b'E')
            sys.exit("谢谢使用")

# 注册
def do_register(s):
    while True:
        # 客户端注册输入的一些操作要求:用户名密码不能有空格，两次密码一致性
        name = input("请输入姓名:")
        passwd = getpass.getpass()
        passwd1 = getpass.getpass('Again:')
        if (' ' in name) or (' ' in passwd):
            print("用户名和密码不允许有空格")
            continue
        if passwd != passwd1:
            print("两次密码输入不一致")
        # 将姓名，密码传给服务器
        msg = 'R {} {}'.format(name, passwd)
        s.send(msg.encode())
        # 等待服务器回复
        data = s.recv(128).decode()
        if data == 'OK':  # 注册成功,返回到调用函数处，由他来显示结果
            return 0
        elif data == 'EXISTS':  # 用户已注册过
            return 1
        else:  # 其他错误
            return 2
# 登录
def do_login(s):
    # 输入姓名密码
    name = input("请输入名字:")
    passwd = getpass.getpass()
    # 将登录标志位，姓名，密码发送给服务端
    msg = 'L {} {}'.format(name, passwd)
    s.send(msg.encode())

    # 等待服务端反馈
    data = s.recv(128).decode()

    if data == 'OK':
        return name
    else:
        return  # 表示返回none

# 登录二次界面与操作
def login(s, name):
    while True:
        print("========== 命令选项 ===========")
        print("********** 1.查词  ************")  # 查单词
        print("*********  2.查历史记录  *******")  # 查看历史查询记录
        print("********** 3.退出  ***********")
        print("==============================")
        try:
            cmd = int(input("请输入命令>>"))
        except Exception as e:
            print("输入错误")
            continue
        if cmd not in [1, 2, 3]:
            print("请输入正确选项")
            sys.stdin.flush()  # 清楚标准输入
            continue

        elif cmd == 1:
            do_query(s, name)  # 传入name是给后面查历史记录做准备
        elif cmd == 2:
            do_hist(s, name)
        elif cmd == 3:
            return


def do_query(s, name):
    while True:
        word = input("你要查的单词")
        if word == '##':
            break
        # 发送查询单词标志位，单词，查询人姓名
        msg = "Q {} {}".format(name, word)
        s.send(msg.encode())
        # 接受反馈结果
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print(data)

        else:
            print("没有查到该单词")


def do_hist(s, name):
    msg = "H {}".format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print("没有历史记录")


if __name__ == "__main__":
    main()
