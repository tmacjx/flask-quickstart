"""
# @Author  wk
# @Time 2020/4/22 10:52

"""
from flask import Blueprint


routes = Blueprint("app", __name__, url_prefix='/api')


@routes.route('/ping', methods=['GET'])
def ping():
    return 'PONG.'


def init_app(app):
    from app.api import auth
    app.register_blueprint(routes)
