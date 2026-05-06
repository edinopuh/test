from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


# форма решения головоломки
class SolveForm(FlaskForm):
    answer = StringField('Ответ:')
    submit = SubmitField('Проверить')
