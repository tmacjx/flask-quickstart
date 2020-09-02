"""
# @Time    : 2020/7/30 11:27
# @Author  : tmackan
"""


class EnumBase(object):
    # APPLE, ORANGE, Banana = range(0, 3)

    @classmethod
    def keys(cls):
        lst = []
        for attr in cls.__dict__:
            if attr.startswith('_') or callable(getattr(cls, attr)):
                continue
            lst.append(attr)
        return lst

    @classmethod
    def values(cls):
        lst = []
        for attr in cls.__dict__:
            if attr.startswith('_') or callable(getattr(cls, attr)):
                continue
            lst.append(getattr(cls, attr))
        return lst

    @classmethod
    def items(cls):
        dct = {}
        for attr, val in cls.__dict__:
            if attr.startswith('_') or callable(getattr(cls, attr)):
                continue
            dct[attr] = val
        return dct
