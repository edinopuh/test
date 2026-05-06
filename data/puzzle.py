import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm, ForeignKey
from .solved_puzzles import user_solved_puzzles


class Puzzle(SqlAlchemyBase):  # модель головоломки
    __tablename__ = 'puzzles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    hint = sqlalchemy.Column(sqlalchemy.String)  # подсказка
    answer = sqlalchemy.Column(sqlalchemy.String)  # правильный ответ
    definition = sqlalchemy.Column(sqlalchemy.Text)  # определение (значение) слова
    user_id = sqlalchemy.Column(sqlalchemy.Integer,  # id автора головоломки
                                ForeignKey('users.id', ondelete='CASCADE'), index=True)
    user = orm.relationship('User', foreign_keys=[user_id], back_populates='puzzles')  # автор голволомки
    solvers = orm.relationship('User', secondary=user_solved_puzzles,  # пользователи, решившие головоломку
                               back_populates='solved_puzzles', lazy='dynamic')
