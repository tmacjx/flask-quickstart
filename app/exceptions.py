"""
# @Time    : 2020/7/30 11:29
# @Author  : tmackan
 业务异常
"""

ERROR_CODES = {
    "ServerError": (11, '系统错误', 'ServerError'),
    "ValidationError": (10, '参数错误', 'Invalid field')

}


class BaseError(Exception):
    raise_alarm = True

    def __init__(self, message=None, payload=None):
        code, msg, msg_en = ERROR_CODES.get(self.__class__.__name__)
        self.code = code
        if message is not None:
            self.message = message
        else:
            self.message = msg
        super(BaseError, self).__init__(message, code, payload)

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.args)


class ServerError(BaseError):
    def __init__(self, message=None, payload=None):
            super(ServerError, self).__init__(message, payload)


class ThirdAPIException(BaseError):
    def __init__(self, message=None, payload=None):
        super(ThirdAPIException, self).__init__(message, payload)


class ValidationError(BaseError):
    raise_alarm = False

    def __init__(self, message=None, payload=None):
        super(ValidationError, self).__init__(message, payload)

