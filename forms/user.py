from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField


class RegistrationForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired(), Length(min=6, max=35)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Зарегистрироваться')


class ConfirmForm(FlaskForm):
    code = StringField('Код подтверждения', validators=[DataRequired()])
    submit = SubmitField('Подтвердить почту')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    # login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
