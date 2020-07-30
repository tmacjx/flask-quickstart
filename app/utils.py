"""
# @Time    : 2020/7/30 17:39
# @Author  : tmackan
"""
import socket
from app import config
from flask import request, abort
import os


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def ip_access_whitelist_check():
    """
    白名单检查
    :return:
    """
    env = os.environ.get('MODE', None)
    # 只检查生产环境
    if env != 'PRODUCTION':
        return
    whitelist = config.IP_WHITELIST
    local_host = get_host_ip()
    request_ip = request.headers.get('X-Real-Ip', request.remote_addr)
    if request_ip == local_host or request_ip in whitelist:
        return
    else:
        abort(403)
