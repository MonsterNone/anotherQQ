from bot import group
from bot import login
from bot import check_all


def login():
    login.login()


def list_groups():
    group.setup()


def list_users(gid):
    group.info('gid', gid)


def get_gid(name):
    group.get_gid(name)


def send(gid, text):
    group.send(gid, text)


def check_login():
    check_all.check()
