"""
# @Author  wk
# @Time 2020/4/22 22:36

"""

# todo 国际化如何去做？
API_STATUS_CODES = {
    # 未知异常 均统一以 系统错误 抛出
    -1: ('系统错误', 'SystemError'),

    # 基础类
    10: '请求参数出错',
    # 已知 但不明确的错误
    11: '操作失败'
}


class APIException(Exception):
    code = -1
    alarm_level = 'error'

    def __init__(self, message=None):
        self._message = message
        super(APIException, self).__init__()

    @property
    def message(self):
        """详细的错误信息"""
        msg_express = self._message if self._message else API_STATUS_CODES.get(self.code, 'Unknown Error')
        return msg_express

    @property
    def warn_message(self):
        """可读的提示错误信息"""
        return API_STATUS_CODES.get(self.code, 'Unknown Error')

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.args)


class APIWarnException(APIException):
    alarm_level = 'warn'
