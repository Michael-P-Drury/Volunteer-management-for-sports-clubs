from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .databases import User
from . import app, lm
from .databases import Jobs
from .forms import SignupForm
from . import db

# from .forms import ... (if you want to import a form)

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/pick_club', methods=['GET', 'POST'])
def pick_club():
    return render_template('pick_club.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/signup')
def signup():
    signup_form = SignupForm()
    return render_template('signup.html', form = signup_form)


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))