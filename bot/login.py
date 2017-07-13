"""
-----------------------------------------------------------------
|                                                               |
|                                                               |
|                         登录、关键参数获取部分                    |
|                         阅读顺序跟随login()函数                  |
|                                                               |
-----------------------------------------------------------------
"""

import re
import time
from .cookie import *
import requests
import sqlite3
from PIL import Image


# 获取二维码
def qr_code():
    # 调用会话
    global r
    # 二维码地址,t后值随意
    url = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.2137678236'
    # 获得返回的二维码图片
    png = r.get(url).content
    # 以二进制模式创建文件并写入
    with open('qrCode.png', 'wb') as pic:
        pic.write(png)
    # 调用PIL的Image库显示图片
    Image.open('qrCode.png').show()


# 等待登录
def wait_login():
    while True:
        sta = status()
        if sta == 0:
            print('等待扫描')
        elif sta == 1:
            print('等待确认')
        elif sta == 2:
            if check_login():
                print('登录成功')
                return True
            else:
                print('登录失败')
                return False
        else:
            print('二维码已失效，请重启')
            exit(0)
        time.sleep(0.5)
    return False


# hash33获取，从TX的js里获取的
def hash33():
    # 将qrsig定义为本函数全局变量
    qrsig = ''
    # 从Cookie中获得qrsig的值
    for i in r.cookies.items():
        if i[0] == 'qrsig':
            qrsig = i[1]
    # 计算hash33
    e = 0
    for i in range(len(qrsig)):
        e = e + (e << 5) + ord(qrsig[i])
    return str(2147483647 & e)


def status():
    # 继续调用会话
    global r
    # 状态获取地址的参数
    params = {
        # ptqrtoken参数
        'ptqrtoken': hash33(),
        # 照抄TX，不用改动
        'webqq_type': 10, 'remember_uin': 1, 'login2qq': 1, 'aid': 501004106,
        'u1': 'http://w.qq.com/proxy.html?login2qq=1', 'ptredirect': 0,
        'ptlang': 2052, 'daid': 164, 'from_ui': 1, 'pttype': 1, 'dumy': '',
        'fp': 'loginerroralert', 'action': '0-0-2983', 'mibao_css': 'm_webqq',
        't': 'undefined', 'g': 1, 'js_type': 0, 'js_ver': 10222, 'login_sig': '',
        'pt_randsalt': 0
    }
    # 不带参数的status获得地址
    url = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
    header = {
        'Referer': 'https://ui.ptlogin2.qq.com/cgi-bin/login?'
                   'daid=164&target=self&style=16&mibao_css=m_webqq'
                   '&appid=501004106&enable_qlogin=0&no_verifyimg=1'
                   '&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&f_url'
                   '=loginerroralert&strong_login=1&login_state=10&'
                   't=20131024001'
    }
    # 全舰装填
    sta = r.get(url, params=params, headers=header).text
    # 状态返回
    if re.search('二维码未失效', sta):
        return 0
    elif re.search('二维码认证中', sta):
        return 1
    elif re.search('登录成功', sta):
        global check_url
        check_url = re.findall("ptuiCB\('0','0','(.*?)','0','登录成功！'", sta)[0]
        return 2
    elif re.search('二维码已失效', sta):
        return 3
    else:
        print('不可描述的错误', sta)
        exit(2)


def check_login():
    global r
    if r.get(check_url, allow_redirects=False).status_code == 302:
        global uin
        uin = re.findall('uin=(.*?)&', check_url)[0]
        print('uin', uin)
        return True
    else:
        return False

def hash2():
    ptb = [0, 0, 0, 0]
    for i in range(len(pt)):
        pt_ind = i % 4
        ptb[pt_ind] = ptb[pt_ind] ^ ord(pt[i])
    uin_byte = [0, 0, 0, 0]
    uin_byte[0] = ((int(uin) >> 24) & 0xFF) ^ ord('E')
    uin_byte[1] = ((int(uin) >> 16) & 0xFF) ^ ord('C')
    uin_byte[2] = ((int(uin) >> 8) & 0xFF) ^ ord('O')
    uin_byte[3] = (int(uin) & 0xFF) ^ ord('K')
    result = [0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(8):
        if i % 2 == 0:
            result[i] = ptb[i >> 1]
        else:
            result[i] = uin_byte[i >> 1]
    h = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    buf = ""
    for i in range(len(result)):
        buf = buf + (h[(result[i] >> 4) & 0xF])
        buf = buf + (h[result[i] & 0xF])
    return buf


def get_sth():
    global pt
    cj = r.cookies.items()
    for i in cj:
        if i[0] == 'ptwebqq':
            pt = i[1]

    global vf
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
    }
    vf = r.get('http://s.web2.qq.com/api/getvfwebqq?ptwebqq=' + pt + '&clientid=53999199&psessionid=&t=144444444',
               headers=header).json()
    if vf['retcode'] != 0:
        print('获取vfwebqq失败，请重试')
        exit(2)
    vf = vf['result']['vfwebqq']

    global ps
    ps_url = 'http://d1.web2.qq.com/channel/login2'
    data = {
        'r': '{"ptwebqq":"' + pt + '","clientid":53999199,"psessionid":"","status":"online"}'
    }
    ps = r.post(ps_url, data=data).json()
    if ps['retcode'] != 0:
        print('获取vfwebqq失败，请重试')
        exit(2)
    ps = ps['result']['psessionid']


# 登录调用主函数
def login():
    # 获得二维码
    print('获取登录二维码中...\n')
    qr_code()
    print('等待二维码扫描...\n')
    if not wait_login():
        print('登录失败\n')
        exit(2)
    get_sth()
    save()


def save():
    cookie.save(r.cookies)
    dict = {
        'pt': pt,
        'ps': ps,
        'vf': vf,
        'uin': uin
    }
    print(dict)
    with open('sth.txt', 'w') as a:
        a.write(str(dict))


# 创建会话储存Cookies
r = requests.session()

# 登录验证网址
check_url = ''

uin = 0
vf = ''
ps = ''
pt = ''
