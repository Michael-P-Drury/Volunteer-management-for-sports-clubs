from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DateField, TimeField, \
    SelectMultipleField, widgets, HiddenField, TextAreaField
from wtforms.validators import input_required, Length, EqualTo, Regexp, NumberRange, Optional

# creates the signup form to be used by routes
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    verify_password = PasswordField('Verify password', validators=[input_required(), EqualTo('password', message='Passwords must match')])
    admin = BooleanField('Admin')
    admin_key = PasswordField('Admin key')
    age_confirm = BooleanField('I confirm I am 13 or over 13')
    submit = SubmitField('Submit')

# creates the login form to be used by routes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[input_required(), Length(1, 20)])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Submit')

# add new announcements form
class AnouncmentForm(FlaskForm):
    announcement_text = TextAreaField('Announcement text', validators=[input_required(), Length(1, 1000)])
    announcement_name = StringField('Announcement name', validators=[input_required(), Length(1, 40)])
    submit = SubmitField('Submit')

#Uses one form for all change fields on profile.
class profileEditForm(FlaskForm):
    form_name = HiddenField(default='profileEditForm')
    new_email = StringField('Enter a new email:', validators=[Optional(),Regexp(regex="[^@]+@[^@]+.[^@]+", message = 'Invalid Email - incorrect format')])
    new_mobile = StringField('Enter a new mobile:', validators=[Optional(),Regexp(regex='^[+-]?[0-9]+$', message = 'Invalid Mobile - integers only'), Length(11, 11)])
    new_dob = StringField('Enter a new date of birth:', validators=[Optional(),Regexp(regex='^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d\d$', message = 'Invalid Date of Birth - incorrect format'), Length(10, 10)])
    new_address = StringField('Enter a new address:', validators=[Optional(),Regexp(regex="^[a-zA-Z0-9\s.,\-/&]+$", message = 'Invalid Address')])
    new_gender = StringField('Enter a new gender:', validators=[Optional(),Regexp(regex='^[a-zA-Z]+$', message = 'Invalid Gender')])
    remove_email = SubmitField('Remove Email')
    remove_mobile = SubmitField('Remove Mobile')
    remove_dob = SubmitField('Remove DOB')
    remove_address = SubmitField('Remove Address')
    remove_gender = SubmitField('Remove Gender')    
    save_changes = SubmitField('Save Changes')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class newJobForm(FlaskForm):
    job_name = StringField('Job name', validators=[input_required()])
    job_description = StringField('Job description', validators=[input_required()])
    volunteers_needed = IntegerField('Number of volunteers needed', validators=[input_required(), NumberRange(min=0)])
    start_time = TimeField('Start time', validators=[input_required()])
    end_time = TimeField('End time', validators=[input_required()])
    date = DateField('Date', validators=[input_required()], format='%Y-%m-%d')
    job_requirements = MultiCheckboxField('Job Requirements', coerce=int)
    submit = SubmitField('Add Job')

class QualificationForm(FlaskForm):
    qualification_name = StringField('Qualification Name', validators=[input_required()])
    qualification_description = StringField('Description', validators=[input_required()])
    submit = SubmitField('Add Qualification')

class ProfileDetailsForm(FlaskForm):
    form_name = HiddenField(default='ProfileDetailsForm')
    new_details = StringField('Detail Text')
    submit5 = SubmitField('Save Details')

