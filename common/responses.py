"""
# @Time    : 2020/7/30 11:32
# @Author  : tmackan
"""

from flask import jsonify


def api_response(data=None,
                 status_code=200, error="invalid"):
    if status_code == 200:
        return data, 200
    else:
        return jsonify({"status": -1, "message": error}), status_code

