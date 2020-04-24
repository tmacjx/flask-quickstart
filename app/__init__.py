"""
# @Author  wk
# @Time 2020/4/22 10:21

"""

__version__ = '1.0.0'

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apidoc import ApiDoc
from flask_cors import CORS
from app.utils import FlaskLogStash, dev_env
from app.config import load_config
from sqlalchemy.exc import DatabaseError
from app.utils import create_redis_connection, RedisClient
from app import api

config = load_config()


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = os.path.join(PROJECT_DIR, 'static')

db = SQLAlchemy()


log_stash = FlaskLogStash()
logger = log_stash.logger


def doc_init_app(app):
    # 开发模式下, 开放文档
    if config.DEBUG:
        ApiDoc(app=app)


redis_conn = create_redis_connection()
redis_client = RedisClient(redis_conn)


def create_app(env_config=config):
    app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/static')
    CORS(app, resources=[r"/api/.*"], origins=r'.*')

    db.init_app(app)
    app.config.from_object(env_config)
    log_stash.init_app(app)
    api.init_app(app)

    @app.teardown_request
    def teardown_request(exception):
        if isinstance(exception, DatabaseError):
            db.session.rollback()
            raise exception
        db.session.remove()
    return app
