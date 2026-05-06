import sqlalchemy
from sqlalchemy import Table, ForeignKey
from .db_session import SqlAlchemyBase

# таблица-посредник для связи "многие ко многим"
user_solved_puzzles = Table(
    'user_solved_puzzles',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('user_id', sqlalchemy.Integer, ForeignKey('users.id'), primary_key=True),
    sqlalchemy.Column('puzzle_id', sqlalchemy.Integer, ForeignKey('puzzles.id'), primary_key=True))
