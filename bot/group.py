from .cookie import *
import sqlite3
import requests
import codecs
from .check_all import *
import time


# 蛇皮占位符
def quote_identifier(s, errors="strict"):
    s = str(s)
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return "\"" + encodable.replace("\"", "\"\"") + "\""


# 从保存的文件中获取参数
def getCookie():
    global r
    global sth
    r.cookies = get(r.cookies)
    with open('bot/sth.txt') as sth:
        sth = eval(sth.read())


def get_groups():
    print('正在获取群列表')
    url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
    data = {
        'r': '{"vfwebqq":"' + sth['vf'] + '","hash":"' + hash2() + '"}'
    }
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
    }
    data = r.post(url, data=data, headers=header).json()
    if data['retcode'] != 0:
        print('错误', data)
        exit(2)
    else:
        print('群列表获取成功，正在储存')
        data = data['result']['gnamelist']
        for i in data:
            cu.execute('INSERT INTO group_list VALUES (?,?,?)', (i['name'], i['gid'], i['code']))
        conn.commit()


def hash2():
    ptb = [0, 0, 0, 0]
    pt = sth['pt']
    uin = sth['uin']
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


def info(type, text):
    gid = 0
    if type == 'name':
        code = cu.execute('SELECT code FROM group_list WHERE name=(?)', (text,)).fetchone()[0]
        gid = cu.execute('SELECT gid FROM group_list WHERE name=(?)', (text,)).fetchone()[0]
    elif type == 'gid':
        gid = int(text)
        code = cu.execute('SELECT code FROM group_list WHERE gid=(?)', (int(gid),)).fetchone()[0]
    elif type == 'code':
        code = int(text)
        gid = cu.execute('SELECT code FROM group_list WHERE code=(?)', (code,)).fetchone()[0]
    else:
        print('type必须是name,gid,code')
        exit(1)
    data = get_info(code)
    try:
        cu.execute(
            'CREATE TABLE ' + quote_identifier(gid) + ' (card char(20) NOT NULL UNIQUE, muin INTEGER UNIQUE NOT NULL)')
    except:
        cu.execute('DROP TABLE ' + quote_identifier(gid))
        cu.execute(
            'CREATE TABLE ' + quote_identifier(gid) + ' (card char(20) NOT NULL UNIQUE, muin INTEGER UNIQUE NOT NULL)')
        pass
    for i in data:
        cu.execute('INSERT INTO ' + quote_identifier(gid) + ' VALUES (?,?)', (i['card'], i['muin']))
    conn.commit()


def get_info(code):
    url = 'http://s.web2.qq.com/api/get_group_info_ext2?gcode=' + str(code) + '&vfwebqq=' + sth[
        'vf'] + '&t=1499952113140'
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id = 1'
    }
    data = r.get(url, headers=header).json()
    if data['retcode'] != 0:
        print('错误', data)
        exit(2)
    else:
        return data['result']['cards']


def get_gid(name):
    gid = cu.execute('SELECT gid FROM group_list WHERE name=(?)', (name,)).fetchone()[0]
    return gid


def setup():
    # 连接数据库
    try:
        cu.execute(
            'CREATE TABLE group_list (name char(20) NOT NULL UNIQUE, gid INTEGER UNIQUE NOT NULL, code INTEGER UNIQUE NOT NULL)')
    except:
        cu.execute('DROP TABLE group_list')
        cu.execute(
            'CREATE TABLE group_list (name char(20) NOT NULL UNIQUE, gid INTEGER UNIQUE NOT NULL, code INTEGER UNIQUE NOT NULL)')
        pass

    getCookie()
    get_groups()
    conn.commit()
    print('储存完毕')


def send(gid, text):
    url = 'https://d1.web2.qq.com/channel/send_qun_msg2'
    header = {
        'Referer': 'https://d1.web2.qq.com/cfproxy.html?v=20151105001&callback=1'
    }
    data = {
        'r': '{"to":' + str(
            gid) + ',"content":"[\\"' + text + '\\",[\\"font\\",{\\"name\\":\\"宋体\\",\\"size\\":10,\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}]]","face":525,"clientid":53999199,"msg_id":' + msg_id() + ',"psessionid":"' +
             sth['ps'] + '"}'
    }
    res = r.post(url, headers=header, data=data).json()
    if not res['msg'] == 'send ok':
        print('发送出错')


def msg_id():
    m_id = int(''.join(str(time.time()).split('.'))[:-4])
    m_id = (m_id - m_id % 1000) / 1000
    m_id = m_id % 10000 * 10000
    m_id = int(m_id + 1)
    return str(m_id)


r = requests.session()
sth = {}
getCookie()
conn = sqlite3.connect('group.db')
cu = conn.cursor()

