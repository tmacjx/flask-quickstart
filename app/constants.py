"""
# @Time    : 2020/7/30 11:28
# @Author  : tmackan
"""

from enum import Enum


class Role(Enum):
    any = "ANY"
    organizer = "ORGANIZER"
    volunteer = "VOLUNTEER"
    track_organizer = "TRACK_ORGANIZER"
    co_organizer = "CO_ORGANIZER"

