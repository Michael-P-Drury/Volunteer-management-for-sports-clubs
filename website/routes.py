from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .databases import User
from . import app, lm
from .databases import Jobs

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def pick_club():
    return render_template('pick_club.html')

@app.route('/')
def home():
    return render_template('home.html')

@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))

