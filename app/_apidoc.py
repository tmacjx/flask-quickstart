"""
# @Author  wk
# @Time 2018/10/16 16:04

#  apidoc 注释宏定义
"""

#    doc文档注释demo 参考: http://apidocjs.com
#    @api {get} /users/:user_id Request User Information
#    @apiVersion 0.1.0
#    @apiName GetUser
#    @apiGroup User
#    @apiPermission admin
#
#    @apiDescription API to get the user information.
#
#    @apiExample Example usage:
#    curl -i http://localhost:5000/users/2
#
#    @apiParam {Number} user_id The user's unique ID.
#
#    @apiSuccess {String} name Name of the User.
#    @apiSuccessExample {json} Success-Response:
#        HTTP/1.1 200 OK
#        {
#            "name": "Tom"
#        }
#
#    @apiError UserNotFound The <code>user_id< /code> of the User was not found.
#
#    @apiErrorExample {json} Error-Response:
#        HTTP/1.1 404 Not Found
#        {
#            "error": "UserNotFound",
#            "message": "User {user_id} doesn't exist"
#        }
#
#    @apiSampleRequest http://localhost:5000/users/:user_id


#  参数param相关设置 可选/默认/范围
#  @api {post} /user/
#  @apiParam {String} [firstname]  Optional Firstname of the User.
#  @apiParam {String} lastname     Mandatory Lastname.
#  @apiParam {String} country="DE" Mandatory with default value "DE".
#  @apiParam {Number} [age=18]     Optional Age with default 18.

# {
#     'result': 'FAIL',
#     'errorMsg': '系统错误',
#     'error': {
#         'type': 'CCAPIException',
#         'message': '系统错误',
#         'code': -1
#     }
# }

# API通用成功
"""
    @apiDefine ApiSuccess
    @apiVersion 1.0.0
    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200  OK
      {'result': 'OK'}
 """

# API通用失败
"""
    @apiDefine ApiFail
    @apiVersion 1.0.0
    @apiErrorExample {json} Error-Response:
        HTTP/1.1 200  OK
       {
           'result': 'FAIL', 
           'errorMsg': '系统错误'
       }
 """

# 定义权限
"""
@apiDefine TOKEN 需要在header中传递 token(登录ticket) clientId(设备唯一标识)
"""


# 定义分组
"""
@apiDefine user user相关
"""










