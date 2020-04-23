"""
# @Author  wk
# @Time 2020/4/22 10:41

"""


class Config(object):
    DEBUG = True
    HOST = '127.0.0.1'

    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost/liveclass?charset=utf8&autocommit=true"
    SQLALCHEMY_POOL_SIZE = 32

    PORT = 9000
    REDIS = []
    REDIS_PASSWORD = ""
    DEFAULT_LOCALE = "zh"
    DEFAULT_TIMEZONE = "Asia/Shanghai"

