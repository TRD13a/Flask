from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = StringField('Содержимое', widget=TextArea())
    submit = SubmitField('Опубликовать')


class AuthorForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Добавить')

class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')