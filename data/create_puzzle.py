from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class CreatePuzzle(FlaskForm):  # форма создания головоломки
    puzzle = FileField('Картинка с головоломкой в формате .png или .jpg',
                       validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
    answer = StringField('Правильный ответ', validators=[DataRequired()])
    hint = StringField('Подсказка угадывающему')  # подсказка
    submit = SubmitField('Добавить')
