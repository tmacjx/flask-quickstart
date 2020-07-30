"""
# @Time    : 2020/7/30 11:32
# @Author  : tmackan
"""


# todo 封装response类
# class Response(object):
#     def __init__(self):
#         pass
#
#     def

def result_ok(data=None, **kwargs):
    result = {"status": 1}
    if data is not None:
        result["data"] = data
    if kwargs:
        result.update(kwargs)
    return result


def result_fail(code=1, msg=None):
    return {"status": 0, "errMsg": msg}


def result_dict(status, msg='失败', data='', **kwargs):
    """
    封装返回格式
    :param status:
    :param msg:
    :param data:
    :param kwargs:
    :return:
    """
    if status:
        # return {'result': 'OK', 'errorMsg': '', 'data': data}
        result = {'result': 'OK', 'data': data}
        result.update(kwargs)
        return result
    else:
        return {'result': 'FAIL', 'errorMsg': msg,
                'error': {
                    'type': 'CCAPIException',
                    'message': msg,
                    'code': -1}
                }

