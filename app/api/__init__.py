"""
# @Author  wk
# @Time 2020/4/22 10:52
  路由URL
"""

from app.api.resources.user import UserResource, UsersResource


def initialize_routes(rest_api):
    rest_api.add_resource(UsersResource, '/users')
    rest_api.add_resource(UserResource, '/users/<int:user_id>')

