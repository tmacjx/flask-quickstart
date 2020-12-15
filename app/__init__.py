"""
# @Author  wk
# @Time 2020/4/22 10:21

"""

__version__ = '1.0.0'

import os

import redis_sentinel_url
from flasgger import Swagger
from flask import Flask
from flask_restful import Api as _Api
from werkzeug.exceptions import HTTPException


from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError

from app.api import initialize_routes
from app.config import load_config
from common.log import FlaskLogStash
from common.utils import RedisClient
from common.lock import LockManager, RedisLockBackend


config = load_config()


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = os.path.join(PROJECT_DIR, 'static')

db = SQLAlchemy()


log_stash = FlaskLogStash()
logger = log_stash.logger


# todo init mq
def init_redis():
    logger.debug("Creating Redis connection (%s)", config.REDIS_URL)
    max_connections = config.REDIS_POOL_SIZE
    client_options = {"retry_on_timeout": True, "decode_responses": True,
                      "socket_keepalive": True, "max_connections": max_connections}

    sentinel, client = redis_sentinel_url.connect(config.REDIS_URL, client_options=client_options)
    return client


# todo 需要测试 是否只捕获flask的error handler
class Api(_Api):
    def error_router(self, original_handler, e):
        """ Override original error_router to only handle HTTPExceptions."""
        if self._has_fr_route() and isinstance(e, HTTPException):
            try:
                return self.handle_error(e)
            except Exception:
                pass  # Fall through to original handler
        return original_handler(e)


rest_api = Api()


redis_conn = init_redis()
redis_client = RedisClient(redis_conn)

distributedLock = LockManager(RedisLockBackend)


def create_app(env_config=config):
    app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/static')

    CORS(app, resources=[r"/api/.*"], origins=r'.*')

    db.init_app(app)
    app.config.from_object(env_config)
    log_stash.init_app(app)
    initialize_routes(rest_api)
    Swagger(app)

    print(app.url_map)

    @app.teardown_request
    def teardown_request(exception):
        if isinstance(exception, DatabaseError):
            db.session.rollback()
            raise exception
        db.session.remove()
    return app


# TODO 此处是否可以不实例化？
current_app = create_app()
