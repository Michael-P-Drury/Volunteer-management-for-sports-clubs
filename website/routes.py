from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .databases import User
from . import app, lm
from .databases import Jobs
from .forms import SignupForm
from .forms import LoginForm
from . import db

# from .forms import ... (if you want to import a form)

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('login', **request.args))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    signup_form = SignupForm()

    if signup_form.validate_on_submit():

        password_in = str(signup_form.password.data)
        username_in = str(signup_form.username.data)
        admin_in = bool(signup_form.admin.data)

        if User.query.filter_by(username=username_in).first() is None:
            User.register(username_in, password_in, admin_in)
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', form=signup_form, exists=True)

    return render_template('signup.html', form=signup_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))