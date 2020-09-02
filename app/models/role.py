"""
# @Time    : 2020/7/31 14:51
# @Author  : tmackan
"""

from .import db
from common.mixins.model_helpers import TimestampMixin, BaseModel


# class Article(Base):
#     __tablename__ = 'articles'
#     id = Column(Integer, primary_key=True)
#     comments = relationship("Comment")
#
#
# class Comment(Base):
#     __tablename__ = 'comments'
#     id = Column(Integer, primary_key=True)
#     article_id = Column(Integer, ForeignKey('articles.id'))


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
