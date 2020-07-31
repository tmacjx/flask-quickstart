"""
# @Author  wk
# @Time 2020/4/22 10:23

"""
from flask.ext.sqlalchemy import SQLAlchemy

from common.mixins.model_helpers import TimestampMixin, BaseModel

db = SQLAlchemy()


class SysUser(TimestampMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32))
    user_password = db.Column(db.String(32))
    user_email = db.Column(db.String(32))
    user_info = db.Column(db.Text, nullable=True)

    __tablename__ = "sys_user"

    def __unicode__(self):
        return u'%s' % self.id

    def __repr__(self):
        return '<SysUser %r>' % self.user_name

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


class SysRole(TimestampMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(32))
    enabled = db.Column(db.Integer)
    create_by = db.Column(db.String(32))

    __tablename__ = "sys_role"
    __table_args__ = (db.UniqueConstraint('role_name', name='role_name'),)

    def __repr__(self):
        return '<SysRole %r>' % self.role_name

    def __unicode__(self):
        return u'%s %s' % (self.id, self.role_name)

    def pack_data(self):
        return self.to_dict()

    @classmethod
    def get_all_by_role_name(cls, role_name):
        result = cls.query.filter_by(role_name=role_name).all()
        return result


class SysUserRole(TimestampMixin, BaseModel):
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









