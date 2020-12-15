"""
# @Time    : 2020/7/31 14:51
# @Author  : tmackan
"""

from .import db
from common.mixins.model_helpers import TimestampMixin


class SysRole(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(32))
    enabled = db.Column(db.Integer)
    create_by = db.Column(db.String(32))

    __tablename__ = "sys_role"
    __table_args__ = (db.UniqueConstraint('role_name', name='role_name'),)

    def __repr__(self):
        return '<SysRole %r>' % self.role_name

    @property
    def serialize(self):
        return {
            "role_name": self.role_name,
            "enabled": self.create_by,
            "create_by": self.create_by
        }
