"""
# @Author  wk
# @Time 2020/4/22 10:47

"""


# todo 如何根据Enum实现更优雅？？

# 定义使用的静态变量
class Base(object):

    @classmethod
    def value_range(cls):
        data = [val for key, val in cls.__dict__.items() if not key.startswith('_')]
        data.sort()
        return data

    @classmethod
    def reverse_key(cls, val):
        for key in cls.__dict__.keys():
            if not key.startswith('_'):
                if getattr(cls, key) == val:
                    return key
        return None

    @classmethod
    def dict_items(cls):
        data = [(key, val) for key, val in cls.__dict__.items() if not key.startswith('_')]
        return dict(data)
