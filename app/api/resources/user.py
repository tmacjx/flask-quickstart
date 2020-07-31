"""
# @Author  wk
# @Time 2020/4/27 14:45

"""
from flask.ext.restful import Resource
# from app.forms import USER_ARGS
from flask.ext.restful import fields, marshal_with
from common.mixins.model_helpers import ServiceDAO
from app.models.user import SysUser as SysUserModel


# Create DAO
class UserDAO(ServiceDAO):
    pass


DAO = UserDAO(SysUserModel)


class UsersResource(Resource):
    def get(self):
        """
        用户列表API
        ---
        tags:
          - users
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


class UserResource(Resource):
    # @marshal_with(USER_ARGS)
    def get(self, user_id):
        """
        用户API
        ---
        tags:
          - user
        parameters:
          - name: user_name
            type: string
            required: true
            description: 用户名
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
            description: 单个用户信息
            schema:
                $ref: '#definition/User'
        :return:
        """
        pass

    def post(self):
        pass
