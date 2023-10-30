from flask_login import UserMixin
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(30))
    mobile = db.Column(db.String(15))
    preferred_name = db.Column(db.String(15))
    qualifications = db.Column(db.String(64))
    events = db.Column(db.String(100))

class jobs(UserMixin, db.Model):
    __tablename__ = 'jobs'
    jobid = db.Column(db.Integer, primary_key=True)
    volunteers_assigned = db.Column(db.String(300))
    volunteers_needed = db.Column(db.Integer)
    times = db.Column(db.String(20))
    date = db.Column(db.String(20))
    job_description = db.Column(db.String(300))
    job_requirements = db.Column(db.String(200))