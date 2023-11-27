from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import input_required, Length, EqualTo, Regexp


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    verify_password = PasswordField('Verify password', validators=[input_required(), EqualTo('password', message='Passwords must match')])
    admin = BooleanField('Admin')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Submit')