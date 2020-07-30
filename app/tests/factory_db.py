"""
# @Author  wk
# @Time 2018/8/7 23:10

   Factory 用于UT SetUp初始化数据

"""
import datetime
import json
from app import db
import app.models


class ModelFactory(object):
    def __init__(self, model, **kwargs):
        self.model = model
        self.kwargs = kwargs

    def _get_kwargs(self, override_kwargs):
        kwargs = self.kwargs.copy()
        kwargs.update(override_kwargs)

        for key, arg in kwargs.items():
            if callable(arg):
                kwargs[key] = arg()

        return kwargs

    def create(self, **override_kwargs):
        kwargs = self._get_kwargs(override_kwargs)
        obj = self.model(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj


user_factory = ModelFactory(app.models.SysUser)

role_factory = ModelFactory(app.models.SysRole)

user_role_factory = ModelFactory(app.models.SysUserRole)


class Factory(object):
    def __init__(self, flag=True):
        self._account = None
        self._room = None
        self._live = None
        self._core()

    def _core(self):
        """
        初始化 账号/房间/直播记录
        :return:
        """
        self._user = self.create_account()
        self._room = self.create_room()
        self._live = self.create_live()
        self.create_atlas_service()

    @property
    def account(self):
        """
        :return:
        """
        if self._account is None:
            self._account = self.create_account()
        return self._account

    @property
    def room(self):
        if self._room is None:
            self._room = self.create_room()
        return self._room

    @property
    def live(self):
        if self._live is None:
            self._live = self.create_live()
        return self._live

    @classmethod
    def create_user(cls, **kwargs):
        """
        :param kwargs:
        :return:
        """
        args = {
        }
        args.update(kwargs)
        return user_factory.create(**args)

    @classmethod
    def create_role(cls, **kwargs):
        """
        :param kwargs:
        :return:
        """








