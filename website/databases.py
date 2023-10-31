from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

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
    admin = db.Column(db.Boolean)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_mobile(self, mobile):
        self.mobile = mobile

    def set_email(self, email):
        self.email = email

    def set_preferred_name(self, preferred_name):
        self.preferred_name = preferred_name

    def set_admin(self, admin):
        self.admin = admin

    @staticmethod
    def register(username, password, email, preferred_name, admin):
        user = User(username=username)
        user.set_password(password)
        user.set_email(email)
        user.set_admin(admin)
        user.set_preferred_name(preferred_name)
        db.session.add(user)
        db.session.commit()
        return user
    def __repr__(self):
        return '<User {0}>'.format(self.username)



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