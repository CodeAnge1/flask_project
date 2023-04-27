import sqlalchemy as sa

from sqlalchemy import orm
from flask_login import UserMixin
from .users_db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    login = sa.Column(sa.String, index=True, unique=True, nullable=False)
    email = sa.Column(sa.String, index=True, unique=True, nullable=False)
    hashed_password = sa.Column(sa.String, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_id(self):
        return self.user_id
