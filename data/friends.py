import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Friend(SqlAlchemyBase, UserMixin):
    __tablename__ = 'friends'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    following = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    followers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    posts = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
