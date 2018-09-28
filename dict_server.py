'''
name:
data:
email:
modules:python pymysql
discribe:电子词典服务端
function:处理客户端的连接请求，具体的操作请求
        在这里单词的查阅是通过文本查阅方式反馈给客户端的
        a,import 模块
        b定义一些需要的全局变量
        c,流程控制
        main()
        连接服务器创建套接字,接收客户端连接,创建新的进程，
        子进程处理请求do_child(connfd,fd)
'''
from socket import *
import os
import time
import signal
import pymysql
import sys

# 定义一些需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST, PORT)

# 流程控制
# 创建套接字,接收客户端连接,创建新的进程
def main():
    # 创建数据库连接
    db = pymysql.connect('localhost', "root", "123456", 'dictory')

    # 创建套接字
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    # 忽略子进程退出信号
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    # 循环等待客户端连接
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:  # 按ctrl+c服务端退出
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("服务器异常:", e)
            continue

        print("已连接客户端:", addr)
        # 如果没有异常连接成功
        # 创建子进程
        pid = os.fork()
        if pid == 0:
            sockfd.close()
            print("子进程准备处理请求")
            # 具体的处理客户请求
            do_child(connfd, db)

        else:
            connfd.close()
            continue

# 具体的处理客户端请求
def do_child(c, db):
    # 循环接受客户端请求
    while True:
        data = c.recv(1024).decode()
        print(c.getpeername(), ":", data)  # 从哪个客户端收到的什么信息
        if (not data) or data[0] == 'E':  # 退出
            c.close()
            sys.exit(0)  # 服务器退出
        elif data[0] == 'R':  # 注册请求标志位
            do_register(c, db, data)
        elif data[0] == 'L':  # 登录请求标志位
            do_login(c, db, data)
        elif data[0] == 'Q':  # 询问查询单词标志位
            do_query(c, db, data)
        elif data[0] == 'H':  # 查询历史记录标志位
            do_hist(c, db, data)

# 处理注册请求
def do_register(c, db, data):
    print("注册操作")
    l = data.split(' ')  # 重点操作，截取客户端发送的信息
    name = l[1]
    passwd = l[2]
    cur = db.cursor()
    sql = "select * from userinfo where name = '%s'" % name
    cur.execute(sql) # 游标对象执行查询操作
    r = cur.fetchone()  # 检索用户信息字典中是否有该用户
    if r != None:  # 如果有返回值的话证明该用户名已注册过
        c.send(b"EXESTS")
        return
    # 该注册用户不存在的时候,向字典中插入该用户信息
    sql = "insert into userinfo (name,password) values \
    ('%s','%s')" % (name, passwd)
    try:
        cur.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()  # 事物回滚
        c.send(b'Fall')
    else:
        print("注册成功" % name)


def do_login(c, db, data):
    print("登录操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cur = db.cursor()
    sql = "select * from userinfo where name = '%s'\
        and password = '%s'" % (name, passwd)
    cur.execute(sql)
    r = cur.fetchone()

    if r == None:
        c.send(b'Fall')
    else:
        print("%s登陆成功" % name)
        c.send(b'OK')


def do_query(c, db, data):
    print("查单词操作")
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cur = db.cursor()
    #将查询记录插入数据库usedword中
    def insert_history():
        tm = time.ctime()  # 字符串

        sql = "insert into usedword (name,word,time)\
        values('%s','%s','%s')" % (name, word, tm)
        try:
            cur.execute(sql)
            db.commit()
        except:
            db.rollback()
# 数据库查询
    #sql = "select value from dictory1 where word = '%s'"%word
# 文本查询
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b'Fall')
        return

    for line in f:
        tmp = line.split(' ')[0]  # 首字母
        if tmp > word:
            c.send(b'Fall')
            f.close()
            return
        elif tmp == word:
            c.send(b'OK')
            time.sleep(0.1)  # 防止粘连
            c.send(line.encode())
            f.close()
            # 调用插入历史数据函数
            insert_history()
            return
    c.send(b'Fall')  # 输入zzzz情况
    f.close()


def do_hist(c, db, data):
    print("历史记录")
    l = data.split(' ')
    name = l[1]
    cur = db.cursor()

    sql = "select * from usedword where name = '%s'" % name
    cur.execute(sql)
    r = cur.fetchall()

    if not r:
        c.send(b'Fall')
        return
    else:
        c.send(b'OK')

    for i in r:
        time.sleep(0.1)
        msg = "%s  %s  %s" % (i[1], i[2], i[3])  # name word time
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')


if __name__ == "__main__":
    main()
