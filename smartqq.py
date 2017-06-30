import re
import json
import time
import sqlite3
import requests
from PIL import Image


# 获取待扫描的二维码并在默认图片浏览器中打开
def qr_code():
    global r
    qr_url = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.2137678236'
    png = r.get(qr_url).content
    with open('qrCode.png', 'wb') as a:
        a.write(png)
    img = Image.open('qrCode.png')
    img.show()


# hash33，从https://imgcache.qq.com/ptlogin/ver/10222/js/mq_comm.js改编而来
def hash33():
    qrsig = ''
    for i in r.cookies.items():
        if i[0] == 'qrsig':
            qrsig = i[1]
    e = 0
    for i in range(len(qrsig)):
        e = e + (e << 5) + ord(qrsig[i])
    return str(2147483647 & e)


# 获取登录状态
def status():
    global r
    params = {
        'ptqrtoken': hash33(),
        # 以下完全照抄
        'webqq_type': 10, 'remember_uin': 1, 'login2qq': 1, 'aid': 501004106,
        'u1': 'http://w.qq.com/proxy.html?login2qq=1', 'ptredirect': 0,
        'ptlang': 2052, 'daid': 164, 'from_ui': 1, 'pttype': 1, 'dumy': '',
        'fp': 'loginerroralert', 'action': '0-0-2983', 'mibao_css': 'm_webqq',
        't': 'undefined', 'g': 1, 'js_type': 0, 'js_ver': 10222, 'login_sig': '',
        'pt_randsalt': 0
    }
    sta_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
    # 好丑啊
    header = {
        'Referer': 'https://ui.ptlogin2.qq.com/cgi-bin/login?'
                   'daid=164&target=self&style=16&mibao_css=m_webqq'
                   '&appid=501004106&enable_qlogin=0&no_verifyimg=1'
                   '&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&f_url'
                   '=loginerroralert&strong_login=1&login_state=10&'
                   't=20131024001'
    }
    return r.get(sta_url, params=params, headers=header).text


# hash2， 从http://pub.idqqimg.com/smartqq/js/mq.js?t=20161220改编而来
def hash2(puin, ptwebqq):
    ptb = [0, 0, 0, 0]
    for i in range(len(ptwebqq)):
        pt_ind = i % 4
        ptb[pt_ind] = ptb[pt_ind] ^ ord(ptwebqq[i])
    uin_byte = [0, 0, 0, 0]
    uin_byte[0] = ((int(puin) >> 24) & 0xFF) ^ ord('E')
    uin_byte[1] = ((int(puin) >> 16) & 0xFF) ^ ord('C')
    uin_byte[2] = ((int(puin) >> 8) & 0xFF) ^ ord('O')
    uin_byte[3] = (int(puin) & 0xFF) ^ ord('K')
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


def msg_id():
    m_id = int(''.join(str(time.time()).split('.'))[:-4])
    m_id = (m_id - m_id % 1000) / 1000
    m_id = m_id % 10000 * 10000
    m_id = int(m_id + 1)
    return str(m_id)


def login():
    qr_code()
    sta = status()
    global r
    print('等待扫描二维码\n')
    while re.search('二维码未失效', sta):
        time.sleep(0.5)
        sta = status()
    if re.search('二维码已失效', sta):
        print('二维码已经失效了，正在重新获取，请尽快扫描新二维码\n')
        for i in range(2):
            qr_code()
            sta = status()
            while re.search('二维码未失效', sta):
                time.sleep(0.5)
                sta = status()
                break
        if re.search('二维码已失效', sta):
            print('你是在逗我玩吗？\n连续三次未扫描二维码，程序退出！')
            exit(0)
        else:
            print('Wrong')
    while re.search('二维码认证中', sta):
        print('等待登录授权')
        time.sleep(0.5)
        sta = status()
    if not re.search('登录成功', sta):
        print('一些不可描述的错误发生了')
        exit(2)
    cookie_url = re.findall("ptuiCB\('0','0','(.*?)','0','登录成功！'", sta)[0]
    if r.get(cookie_url, allow_redirects=False).status_code == 302:
        print('扫描成功！')
    else:
        print('一些不可描述的错误发生了')
        exit(2)

    cj = r.cookies.items()
    global pt
    for i in cj:
        if i[0] == 'ptwebqq':
            pt = i[1]
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
    }
    global vf
    vf = r.get('http://s.web2.qq.com/api/getvfwebqq?ptwebqq=' + pt + '&clientid=53999199&psessionid=&t=144444444',
               headers=header).json()
    if vf['retcode'] != 0:
        print('获取vfwebqq失败，请重试')
        exit(2)
    vf = vf['result']['vfwebqq']
    ps_url = 'http://d1.web2.qq.com/channel/login2'
    data = {
        'r': '{"ptwebqq":"' + pt + '","clientid":53999199,"psessionid":"","status":"online"}'
    }
    global ps
    ps = r.post(ps_url, data=data).json()
    if ps['retcode'] != 0:
        print('获取vfwebqq失败，请重试')
        exit(2)
    ps = ps['result']['psessionid']
    global uin
    uin = re.findall('uin=(.*?)&', cookie_url)[0]


def check_login():
    if pt == '' or ps == '' or uin == 0:
        print('未登录，请先通过smartbot.login()登录')
        exit(0)


# 通过sqlite3储存数据
def friends():
    check_login()
    global uin
    global r
    print('正在获取好友列表')
    data = {
        'r': '{"vfwebqq":"' + vf + '","hash":"' + hash2(uin, pt) + '"}'
    }
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
    }
    fri = r.post('http://s.web2.qq.com/api/get_user_friends2', headers=header, data=data).json()['result']
    friends = fri['friends']
    categories = fri['categories']
    marknames = fri['marknames']
    info = fri['info']

    # 写入数据库
    open('friends.db', 'w').close()
    conn = sqlite3.connect('friends.db')
    cu = conn.cursor()

    cu.execute('CREATE TABLE categories (ind INTEGER UNIQUE,cname var char(10))')
    cu.execute('CREATE TABLE marknames (uin INTEGER UNIQUE,markname var char(20))')
    cu.execute('CREATE TABLE info (uin INTEGER UNIQUE,nick var char(20))')
    cu.execute('INSERT INTO categories VALUES (0,"我的好友")')

    for i in categories:
        cu.execute('INSERT INTO categories VALUES (?,?)', (i['index'], i['name']))
    for j in marknames:
        cu.execute('INSERT INTO marknames VALUES (?,?)', (j['uin'], j['markname']))
    for k in info:
        cu.execute('INSERT INTO info VALUES (?,?)', (k['uin'], k['nick']))

    cu.execute('CREATE TABLE friends (uin INTEGER UNIQUE,mark var char(20),category var char(10))')
    for u in friends:
        ind = u['categories']
        uin = u['uin']
        category = cu.execute('SELECT cname FROM categories WHERE ind=(?);', (ind,)).fetchone()
        mark = cu.execute('SELECT markname FROM marknames WHERE uin=(?);', (uin,)).fetchone()
        if mark == None:
            mark = cu.execute('SELECT nick FROM info WHERE uin=(?);', (uin,)).fetchone()
        cu.execute('INSERT INTO friends VALUES (?,?,?);', (uin, mark[0], category[0]))

    cu.execute('DROP TABLE categories')
    cu.execute('DROP TABLE marknames')
    cu.execute('DROP TABLE info')
    conn.commit()
    conn.close()


def receive():
    global r
    check_login()
    header = {
        'Referer': 'https://d1.web2.qq.com/cfproxy.html?v=20151105001&callback=1'
    }
    data = {
        'ptwebqq': pt,
        'clientid': 53999199,
        'psessionid': ps,
        'key': ''
    }
    data = 'r="' + json.dumps(data) + '"'
    mess = r.post('https://d1.web2.qq.com/channel/poll2', headers=header, data=data).json()
    if mess['retcode'] != 0:
        print('接受消息时出现了一个错误！')
        print(mess)
        exit(2)
    while not mess:
        mess = r.post('https://d1.web2.qq.com/channel/poll2', headers=header, json=json).json()
        time.sleep(1)
    if mess:
        mess = mess['result'][0]['value']
        back = {}
        back['text'] = mess['content'][1]
        back['from'] = mess['from_uin']
        return back


def send(to_uin, text):
    time.sleep(0.5)
    global r
    header = {
        'Referer': 'https://d1.web2.qq.com/cfproxy.html?v=20151105001&callback=1'
    }
    data = {
        'r': '{"to":'+str(to_uin)+',"content":"[\\"'+text+'\\",[\\"font\\",{\\"name\\":\\"宋体\\",\\"size\\":10,\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}]]","face":525,"clientid":53999199,"msg_id":' + msg_id() + ',"psessionid":"' + ps + '"}'
    }
    sta = r.post('https://d1.web2.qq.com/channel/send_buddy_msg2', headers=header, data=data).json()
    print(type(sta['errCode']))
    if sta['msg']:
        if sta['msg'] == 'send ok':
            print('发送成功')
    else:
        print('消息发送失败，请检查')
        print(sta)


def getuin(mark):
    conn = sqlite3.connect('friends.db')
    cu = conn.cursor()
    u = cu.execute('SELECT uin FROM friends WHERE mark=(?)',(mark,))
    if not u:
        print('没有这个人')
    else:
        return u.fetchone()[0]


def getcate(fuin):
    conn = sqlite3.connect('friends.db')
    cu = conn.cursor()
    u = cu.execute('SELECT category FROM friends WHERE uin=(?)',(fuin,))
    if not u:
        print('没有这个人')
    else:
        return u.fetchone()[0]

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'https://127.0.0.1:8080'
}

r = requests.session()

# 全局变量ptwebqq, vfwebqq, psessionid
pt = ''
vf = ''
ps = ''
uin = 0

login()
friends()