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

class Jobs(UserMixin, db.Model):
    __tablename__ = 'jobs'
    jobid = db.Column(db.Integer, primary_key=True)
    volunteers_assigned = db.Column(db.String(300))
    volunteers_needed = db.Column(db.Integer)
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    date = db.Column(db.String(20))
    job_description = db.Column(db.String(300))
    job_requirements = db.Column(db.String(200))

    def clear_volunters(self):
        self.volunteers = ''

    def assign_times(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def assign_date(self, date):
        self.date = date

    def assign_description(self, job_description):
        self.job_description = job_description

    def assign_requirements(self, job_requirements):
        self.job_requirements = job_requirements

    def assign_volunteers_needed(self, volunteers_needed):
        self.volunteers_needed = volunteers_needed

    @staticmethod
    def add_new_job(volunteers_needed, start_time, end_time, date, job_description, job_requirements):
        job = Jobs()
        job.clear_volunters()
        job.assign_times(start_time, end_time)
        job.assign_date(date)
        job.assign_description(job_description)
        job.assign_requirements(job_requirements)
        job.assign_volunteers_needed(volunteers_needed)
        db.session.add(job)
        db.session.commit()
        return job







