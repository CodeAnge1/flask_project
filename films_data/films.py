import sqlalchemy as sa

from sqlalchemy import orm
from .films_db_session import SqlAlchemyBase


class Film(SqlAlchemyBase):
    __tablename__ = 'films'
    film_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    original_name = sa.Column(sa.String, nullable=True)
    rating = sa.Column(sa.Float, nullable=True)
    duration = sa.Column(sa.String, nullable=True)
    country = sa.Column(sa.String, nullable=True)
    genres = sa.Column(sa.String, nullable=True)
    year = sa.Column(sa.Integer)
    poster_link = sa.Column(sa.String, nullable=True)
    trailer_link = sa.Column(sa.String, nullable=True)
    type_of_film = sa.Column(sa.String, nullable=True)
    source_link = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=True)
    high_poster_link = sa.Column(sa.String, nullable=True)
    # medias = orm.relationship("Media", back_populates='film')
