"""
# @Author  wk
# @Time 2020/4/22 22:39

"""
from app.exception import APIWarnException

from flask_babel import format_datetime


# todo 国际化怎么做？
class UserBaned(APIWarnException):
    """
    账号封禁
    """
    code = 1001
    info = ("账户封禁", 'userBand')
