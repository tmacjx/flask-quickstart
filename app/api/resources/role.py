"""
# @Author  wk
# @Time 2020/4/27 14:45

"""
from flask.ext.restful import Resource
from app.models.role import SysRole as SysRoleModel
from common.mixins.model_helpers import ServiceDAO


class RoleDAO(ServiceDAO):
    pass


DAO = RoleDAO(SysRoleModel)


class RoleResource(Resource):
    def get(self):
        """
        角色列表API
        ---
        tags:
          - roles
        definition:
            User:
              type: Object
              properties:
                id:
                  type: string
                  description: 用户ID
                user_name:
                  type: string
                  description: 用户名
                user_email:
                  type: string
                  description: 用户邮箱
                user_info:
                  type: string
                  description: 用户信息
        responses:
          200:
            description: 用户列表
            schema:
              properties:
                type: array
                items:
                    $ref: '#/definitions/User'
        :return:
        """
        return DAO.first()
