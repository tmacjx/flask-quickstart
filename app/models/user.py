"""
# @Time    : 2020/7/31 14:51
# @Author  : tmackan
"""

from .import db
from common.mixins.model_helpers import TimestampMixin, BaseModel


class SysUser(TimestampMixin, db.Model):
    __tablename__ = "sys_user"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32))
    user_password = db.Column(db.String(32))
    user_email = db.Column(db.String(32))
    user_info = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<SysUser %r>' % self.user_name

    @property
    def serialize(self):
        return {
            "user_name": self.user_name,
            "user_password": self.user_password,
            "user_email": self.user_email,
            "user_info": self.user_info
        }


class SysUserRole(TimestampMixin, BaseModel):
    __tablename__ = "sys_user_role"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("sys_user.id"))
    user = db.relationship(SysUser, backref='user', foreign_keys=[user_id])
    role_id = db.Column(db.Integer, db.ForeignKey("sys_role.id"))
    role = db.relationship("SysRole", backref='role', foreign_keys=[role_id])

    def __repr__(self):
        return '<SysUserRole %r>' % self.user_id

    @property
    def serialize(self):
        return {
            "user_id": self.user_id,
            "role_id": self.role_id
        }
