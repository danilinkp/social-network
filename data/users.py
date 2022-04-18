import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='write about yourself')
    second_email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    github = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, default="default.jpg")
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    followings = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')

    followers = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    post_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    admin_check = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
