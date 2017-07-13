from .login import *
from .cookie import *
import requests

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https': 'https://127.0.0.1:8080'
}

# 从保存的文件中获取参数
def getCookie():
    global r
    global sth
    r.cookies = get(r.cookies)
    with open('bot/sth.txt') as sth:
        sth = eval(sth.read())


def get_groups():
    url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
    data = {
        'r': '{"vfwebqq":"' + sth['vf'] + '","hash":"' + hash2() + '"}'
    }
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
    }
    res = r.post(url, data=data, headers=header).json()
    if res['retcode'] != 0:
        print(res)
        return False
    elif res['retcode'] == 0:
        return True
    else:
        print('不可描述的登录检查错误')
        exit(2)


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

def friends():
    print('正在获取好友列表')
    data = {
        'r': '{"vfwebqq":"' + sth['vf'] + '","hash":"' + hash2() + '"}'
    }
    header = {
        'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
    }
    fri = r.post('http://s.web2.qq.com/api/get_user_friends2', headers=header, data=data).json()
    if fri['retcode'] != 0:
        print('失败')
        return False
    return True

def check():
    getCookie()
    if get_groups():
        print('成功')
    else:
        print('失效，重新登录')
        login()


# login.login()
r = requests.session()
check()
