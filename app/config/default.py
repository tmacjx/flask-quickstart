"""
# @Author  wk
# @Time 2020/4/22 10:41

"""


class Config(object):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 9000

    LOG_LEVEl = "INFO"
    LOG_PATH = "/tmp/app.log"
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost/test?charset=utf8&autocommit=true"
    SQLALCHEMY_POOL_SIZE = 32

    DEFAULT_LOCALE = "zh"
    DEFAULT_TIMEZONE = "Asia/Shanghai"
    REDIS_URL = "redis://test:123456@localhost:6379/0"
    REDIS_sentinel_URL = "redis+sentinel://test:test@localhost:6379/0;"
    REDIS_POOL_SIZE = 200


