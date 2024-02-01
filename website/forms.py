from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import input_required, Length, EqualTo, Regexp

# creates the signup form to be used by routes
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    verify_password = PasswordField('Verify password', validators=[input_required(), EqualTo('password', message='Passwords must match')])
    admin = BooleanField('Admin')
    submit = SubmitField('Submit')

# creates the login form to be used by routes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Submit')

# form for changing/ adding email
class emailChangeForm(FlaskForm):
    new_email = StringField('Enter a new email:', validators=[Regexp(regex="[^@]+@[^@]+.[^@]+", message = 'has to be a valid email'), input_required()])
    submit1 = SubmitField('Submit')

# form for changing/ adding mobile number
class mobileChangeForm(FlaskForm):
    new_mobile = StringField('Enter a new mobile:', validators=[Regexp(regex='^[+-]?[0-9]+$', message = 'only integers allowed'), input_required(), Length(11, 11)])
    submit2 = SubmitField('Submit')

class removeEmail(FlaskForm):
    submit3 = SubmitField('Remove email?')

class removeMobile(FlaskForm):
    submit4 = SubmitField('Remove mobile?')


