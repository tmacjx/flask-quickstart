"""
# @Author  wk
# @Time 2018/7/30 10:10

    UT Fixtures
"""

import pytest
from webtest import TestApp

from app import create_app, db as _db
from app.config.test import TestConfig
from app.tests.factory_db import Factory


@pytest.yield_fixture(scope='session')
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='session')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture(scope='session')
def db_source(db):
    model_factory = Factory(flag=True)
    account = model_factory.account
    room = model_factory.room
    # 默认未开启直播
    live = model_factory.live
    return model_factory, account, room, live


@pytest.fixture()
def config(request, init_config):
    """
    clean up account/room状态
    :param request:
    :return:
    """

    yield

    def fin():
        _db.session.commit()
    request.addfinalizer(fin)


