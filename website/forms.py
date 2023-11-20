from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import input_required, Length, EqualTo, Regexp

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    verifyPassword = PasswordField('Verify password', validators=[input_required(), EqualTo('password', message='Passwords must match')])
    email = StringField('email', validators=[Regexp(regex="[^@]+@[^@]+.[^@]+", message='has to be a valid email'),input_required()])
    prefered_name = StringField('Preferred name', validators=[input_required(), Length(1, 20)])
    admin = BooleanField('Admin')
    submit = SubmitField('Submit')