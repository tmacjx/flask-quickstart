"""
# @Author  wk
# @Time 2020/4/22 10:23

"""


from sqlalchemy.orm.attributes import QueryableAttribute
import json
from app import db, logger
from app.utils import JSONEncoder


class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self, only=None, exclude=None):
        """
        :param only: 如果存在，则只显示 show中的字段
        :param exclude: 过滤字段
        :return:
        """
        table_columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        model_properties = list(set(dir(self)) - set(table_columns) - set(relationships))
        default_filed_list = table_columns + model_properties

        if only is not None:
            fields_list = list(only)
        elif exclude is not None:
            exclude_list = list(exclude)
            if hasattr(self, "__exclude_fields__"):
                exclude_list += list(getattr(self, "__exclude_fields__"))
            fields_list = default_filed_list - exclude_list
        else:
            fields_list = default_filed_list

        ret_data = {}

        for key in fields_list:
            if key.startswith("_"):
                continue
            if key not in dir(self):
                raise TypeError('%s does not have an attribute %s' % (self, key))
            # 如果是column
            if key in table_columns:
                ret_data[key] = getattr(self, key)
            # 如果是property
            if key in model_properties:
                attr = getattr(self.__class__, key)
                if isinstance(attr, property) or isinstance(attr, QueryableAttribute):
                    val = getattr(self, key)
                else:
                    continue
                if hasattr(val, "to_dict"):
                    ret_data[key] = val.to_dict()
                else:
                    ret_data[key] = val
        return ret_data

    def to_json(self, only=None, exclude=None):
        data = self.to_dict(only=only, exclude=exclude)
        return json.dumps(data, cls=JSONEncoder)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        data = json_dict
        return cls(**data)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            data = dict(data)
        return cls(**data)


class CRUDMixin(object):
    """
    SQLAlchemy相关抽象Mixin
    Main methods:

        create - 新增
        create_batch - 批量新增
        get_or_create - 如果查不到，则新建
        update - 更新
        save - 保存
        delete - 删除
    """
    @classmethod
    def create(cls, commit=True, **kw):
        instance = cls(**kw)
        return instance.save(commit)

    @classmethod
    def create_batch(cls, orm_list):
        db.session.add_all(orm_list)
        return db.session.commit()

    @classmethod
    def get_or_create(cls, commit=True, **kw):
        instance = cls.query.filter_by(**kw).first()
        if not instance:
            instance = cls.create(commit, **kw)
        return instance

    @classmethod
    def get(cls, **kw):
        ret = cls.query.filter_by(**kw)
        if len(ret):
            return ret[0]

    @classmethod
    def gets(cls, **kw):
        return cls.query.filter_by(**kw)

    @classmethod
    def count(cls, **kw):
        return cls.query.filter_by(**kw).count()

    def update(self, commit=True, **kw):
        for attr, value in kw.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit() or self

    @classmethod
    def deletes(cls, **kwargs):
        rs = cls.gets(**kwargs)
        for r in rs:
            r.delete()


class TimestampMixin(object):
    updated_at = db.Column(db.DateTime(True), default=db.func.now(),
                           onupdate=db.func.now(), nullable=False)
    created_at = db.Column(db.DateTime(True), default=db.func.now(),
                           nullable=False)


class SysUser(TimestampMixin, CRUDMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32))
    user_password = db.Column(db.String(32))
    user_email = db.Column(db.String(32))
    user_info = db.Column(db.Text, nullable=True)

    __tablename__ = "sys_user"

    def __unicode__(self):
        return u'%s' % self.id

    def pack_data(self):
        d = self.to_dict()
        d["role"] = SysUserRole.get_role_by_userid(self.id)
        return d

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.filter(cls.id == _id).one()

    @classmethod
    def all(cls):
        result = cls.query.all()
        return result


class SysRole(TimestampMixin, CRUDMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(32))
    enabled = db.Column(db.Integer)
    create_by = db.Column(db.String(32))

    __tablename__ = "sys_role"
    __table_args__ = (db.UniqueConstraint('role_name', name='role_name'),)

    def __unicode__(self):
        return u'%s %s' % (self.id, self.role_name)

    def pack_data(self):
        return self.to_dict()

    @classmethod
    def get_all_by_role_name(cls, role_name):
        result = cls.query.filter_by(role_name=role_name).all()
        return result


class SysUserRole(TimestampMixin, CRUDMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("sys_user.id"))
    user = db.relationship(SysUser, backref='user', foreign_keys=[user_id])
    role_id = db.Column(db.Integer, db.ForeignKey("sys_role.id"))
    role = db.relationship(SysRole, backref='role', foreign_keys=[role_id])

    __tablename__ = "sys_user_role"

    def __unicode__(self):
        return u'%s %s %s' % (self.id, self.user_id, self.role_id)

    def pack_data(self):
        return self.to_dict()

    @classmethod
    def get_role_by_userid(cls, user_id):
        sys_user_role = cls.query.filter_by(user_id=user_id).first()
        if sys_user_role:
            return sys_user_role.role
        else:
            return None









