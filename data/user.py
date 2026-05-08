import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import orm
from .solved_puzzles import user_solved_puzzles


# модель пользователя
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)  # фамилия
    name = sqlalchemy.Column(sqlalchemy.String)  # имя
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)  # почта
    hashed_password = sqlalchemy.Column(sqlalchemy.String)  # пароль (хешированный)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема(dark/light)
    puzzles = orm.relationship(
        'Puzzle',
        foreign_keys='Puzzle.user_id',
        back_populates='user',
    )  # головоломки, созданные пользователем
    solved_puzzles = orm.relationship(
        'Puzzle',
        secondary=user_solved_puzzles,
        back_populates='solvers',
        lazy='dynamic'
    )  # головоломки, которые пользователь решил

    def set_password(self, password):  # хеширование пароля
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # проверка пароля
        return check_password_hash(self.hashed_password, password)
