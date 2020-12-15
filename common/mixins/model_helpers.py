"""
# @Time    : 2020/7/31 11:51
# @Author  : tmackan

  models较多时 需要将models改为目录结构 方便管理

"""
from app.models import db
import json
import logging
from sqlalchemy.orm.attributes import QueryableAttribute
from flask import abort
from common.utils import JSONEncoder
import traceback


logger = logging.getLogger(__name__)


class TimestampMixin(object):
    updated_at = db.Column(db.DateTime(True), default=db.func.now(),
                           onupdate=db.func.now(), nullable=False)
    created_at = db.Column(db.DateTime(True), default=db.func.now(),
                           nullable=False)


# class BaseModel(db.Model):
#     __abstract__ = True
#
#     def to_dict(self, only=None, exclude=None):
#         """
#         :param only: 如果存在，则只显示 show中的字段
#         :param exclude: 过滤字段
#         :return:
#         """
#         table_columns = self.__table__.columns.keys()
#         relationships = self.__mapper__.relationships.keys()
#         model_properties = list(set(dir(self)) - set(table_columns) - set(relationships))
#         default_filed_list = table_columns + model_properties
#
#         if only is not None:
#             fields_list = list(only)
#         elif exclude is not None:
#             exclude_list = list(exclude)
#             if hasattr(self, "__exclude_fields__"):
#                 exclude_list += list(getattr(self, "__exclude_fields__"))
#             fields_list = default_filed_list - exclude_list
#         else:
#             fields_list = default_filed_list
#
#         ret_data = {}
#
#         for key in fields_list:
#             if key.startswith("_"):
#                 continue
#             if key not in dir(self):
#                 raise TypeError('%s does not have an attribute %s' % (self, key))
#             # 如果是column
#             if key in table_columns:
#                 ret_data[key] = getattr(self, key)
#             # 如果是property
#             if key in model_properties:
#                 attr = getattr(self.__class__, key)
#                 if isinstance(attr, property) or isinstance(attr, QueryableAttribute):
#                     val = getattr(self, key)
#                 else:
#                     continue
#                 if hasattr(val, "to_dict"):
#                     ret_data[key] = val.to_dict()
#                 else:
#                     ret_data[key] = val
#         return ret_data
#
#     def to_json(self, only=None, exclude=None):
#         data = self.to_dict(only=only, exclude=exclude)
#         return json.dumps(data, cls=JSONEncoder)
#
#     @classmethod
#     def from_json(cls, json_str):
#         json_dict = json.loads(json_str)
#         data = json_dict
#         return cls(**data)
#
#     @classmethod
#     def from_dict(cls, data):
#         if not isinstance(data, dict):
#             data = dict(data)
#         return cls(**data)


def save_to_db(item, msg):
    """Convenience function to wrap a proper DB save
    :param item: will be saved to database
    :param msg: Message to log
    """
    try:
        logger.info(msg)
        db.session.add(item)
        logger.info('added to session')
        db.session.commit()
        return True
    except Exception as e:
        logger.error('DB Exception! %s' % e)
        traceback.print_exc()
        db.session.rollback()
        return False


def delete_from_db(item, msg):
    """Convenience function to wrap a proper DB delete
    :param item: will be removed from database
    :param msg: Message to log
    """
    try:
        logger.info(msg)
        db.session.delete(item)
        logger.info('removed from session')
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        logger.error('DB Exception! %s' % e)
        db.session.rollback()
        return False


def _error_abort(code, message):
    """Abstraction over restplus `abort`.
    Returns error with the status code and message.
    """
    error = {
        'code': code,
        'message': message
    }
    abort(code, error=error)


# TODO 需要测试
def paginate(query_set, page, page_size):
    """
    分页 封装返回数据
    :param query_set:
    :param page:
    :param page_size:
    :return:
    """
    total = query_set.count()

    if page < 1:
        _error_abort(400, message='Page must be positive integer.')

    if (page - 1) * page_size + 1 > total > 0:
        _error_abort(400, message='Page is out of range.')

    if page_size > 250 or page_size < 1:
        _error_abort(400, message='Page size is out of range (1-250).')

    results = query_set.paginate(page, page_size)
    return {
        'total': total,
        'current': page,
        'size': page_size,
        "pages": results.pages,
        'records': [result for result in results.items],
    }


# TODO 需要测试
def get_paginated_list(klass, args, **kwargs):
    """
    根据前端传的page/page_size
    查询封装分页数据
    :param klass:
    :param args:
    :param kwargs:
    :return:
    """
    queryset = _get_queryset(klass)
    query_set = queryset.filter_by(**kwargs)
    page = args['page']
    page_size = args['page_size']
    results = paginate(query_set, page, page_size)
    return results


def _get_queryset(klass):
    """Returns the queryset for `klass` model"""
    return klass.query


def get_object_list(klass, **kwargs):
    """Returns a list of objects of a model class. Uses other passed arguments
    with `filter_by` to filter objects.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj_list = list(queryset.filter_by(**kwargs))
    return obj_list


def get_object_first(klass, **kwargs):
    queryset = _get_queryset(klass)
    obj = queryset.filter_by(**kwargs).first()
    return obj


def get_list_or_404(klass, **kwargs):
    """Abstraction over `get_object_list`.
    Raises 404 error if the `obj_list` is empty.
    """
    obj_list = get_object_list(klass, **kwargs)
    if not obj_list:
        _error_abort(404, 'Object list is empty')
    return obj_list


def get_or_create(klass, **kwargs):
    instance = db.session.query(klass).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = klass(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance


def get_object_or_404(klass, id_):
    """Returns a specific object of a model class given its identifier. In case
    the object is not found, 404 is returned.
    `klass` can be a model such as a Track, Event, Session, etc.
    """
    queryset = _get_queryset(klass)
    obj = queryset.get(id_)
    if obj is None:
        _error_abort(404, '{} does not exist'.format(klass.__name__))
    return obj


def create_service_model(model, data):
    new_model = model(**data)
    save_to_db(new_model, "Model %s saved" % model.__name__)
    return new_model


def delete_service_model(model, id_):
    """
    Delete a service model.
    """
    item = get_object_or_404(model, id_)
    delete_from_db(item, '{} deleted'.format(model.__name__))
    return item


def update_model(model, item_id, data):
    """
    Updates a model
    """
    item = get_object_or_404(model, item_id)
    db.session.query(model).filter_by(id=item_id).update(dict(data))
    # model.__table__.update().where(model.id==item_id).values(**data)
    save_to_db(item, "%s updated" % model.__name__)
    return item


# todo 是否引入缓存
class ServiceDAOCache(object):
    pass


class ServiceDAO(object):
    """
    Data Access Object for service models
    """
    def __init__(self, model):
        self.model = model

    def get(self, id_):
        return get_object_or_404(self.model, id_)

    def first(self, **kwargs):
        return get_object_first(self.model, **kwargs)

    def list(self, **kwargs):
        return get_object_list(self.model, **kwargs)

    def one(self, **kwargs):
        return get_object_first(self.model, **kwargs)

    def create(self, data):
        item = create_service_model(self.model, data)
        return item

    def update(self, id_, data):
        item = update_model(self.model, id_, data)
        return item

    def delete(self, id_):
        item = delete_service_model(self.model, id_)
        return item

