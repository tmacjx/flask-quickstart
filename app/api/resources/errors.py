"""
# @Time    : 2020/7/30 19:04
# @Author  : tmackan
"""
from flask import jsonify
from app.exceptions import ServerError, ValidationError

from app import rest_api


@rest_api.errorhandler(ValidationError)
def handle_bad_request(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['code'] = error.code
    payload['message'] = error.message

    # todo 引发报警 报警信息如何处理
    return jsonify(payload), 200


@rest_api.errorhandler
def default_error_handler(error):
    """Returns Internal server error"""
    error = ServerError()
    payload = {"code": error.code, "message": error.message}
    return jsonify(payload, 500)


