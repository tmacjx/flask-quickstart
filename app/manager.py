"""
# @Time    : 2020/7/30 17:02
# @Author  : tmackan
    ORM Manager DAO层 业务查询相关
    多个model的相互操作封装
"""

from common.mixins.model_helpers import save_to_db, delete_from_db, get_or_create
from .models.user import SysUser, SysUserRole
from .models.role import SysRole


class DataManager(object):
    """
    多model关联相关的操作 add/update/delete
    """
    @staticmethod
    def create_user():
        pass


class DataGetter(object):
    """
    model 相关的query
    """
    @staticmethod
    def get_user():
        pass

