"""
# @Author  wk
# @Time 2020/4/22 10:47

"""
from enum import Enum


# member = Color.red
# member.name
# member.value
# [mem.value for mem in Color]

class UserStatus(Enum):
    active = 1
    inactive = 0


class Status(Enum):
    status = 1
    close = 0
