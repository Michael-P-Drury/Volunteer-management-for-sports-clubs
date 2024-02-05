from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

# creates the user table which stores user's information
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(30))
    mobile = db.Column(db.String(15))
    preferred_name = db.Column(db.String(15))
    qualifications = db.Column(db.String(64))
    events = db.Column(db.String(100))
    admin = db.Column(db.Boolean)

    # gets the current users id
    def get_id(self):
        return str(self.user_id)

    # sets passwords hashes and sets the current password to the hash creatde
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # checks that the password inputted is correct
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # sets the mobile number inputted
    def set_mobile(self, mobile):
        self.mobile = mobile

    # sets email inputted
    def set_email(self, email):
        self.email = email

    # sets preferred name of user as inputted
    def set_preferred_name(self, preferred_name):
        self.preferred_name = preferred_name

    # sets admin statas as inputted
    def set_admin(self, admin):
        self.admin = admin

    # sets mobile number to blank
    def no_mobile(self):
        self.mobile = None

    # sets qualifications to blank
    def no_qualifications(self):
        self.qualifications = None

    # sets the users events to blank
    def no_events(self):
        self.events = None

    # sets the preferred name of teh user to blank
    def no_preferred_name(self):
        self.preferred_name = None

    # sets email to blank
    def no_email(self):
        self.email = None

    # registeres a new user
    @staticmethod
    def register(username, password, admin):
        user = User(username=username)
        user.set_password(password)
        user.no_email()
        user.set_admin(admin)
        user.no_mobile()
        user.no_events()
        user.no_qualifications()
        user.no_preferred_name()
        db.session.add(user)
        db.session.commit()
        return user

    # needed for getting users
    def __repr__(self):
        return '<User {0}>'.format(self.username)


# creates the job table which stores all the jobs
class Jobs(UserMixin, db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(20))
    volunteers_assigned = db.Column(db.String(300))
    volunteers_needed = db.Column(db.Integer)
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    date = db.Column(db.String(20))
    job_description = db.Column(db.String(300))
    job_requirements = db.Column(db.String(200))

    # clears volunteers from one of the jobs
    def clear_volunters(self):
        self.volunteers = ''

    # assigns start and end times to the job
    def assign_times(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    # assigns a date to the job
    def assign_date(self, date):
        self.date = date

    # assigns a job description to the job
    def assign_description(self, job_description):
        self.job_description = job_description

    # assigns requirements to the job
    def assign_requirements(self, job_requirements):
        self.job_requirements = job_requirements

    # assigns the number of volunteers needed to a job
    def assign_volunteers_needed(self, volunteers_needed):
        self.volunteers_needed = volunteers_needed

    # assignes job name
    def assign_job_name(self, new_job_name):
        self.job_name = new_job_name


    # creates a new job with the information passed into it
    @staticmethod
    def add_new_job(job_name, volunteers_needed, start_time, end_time, date, job_description, job_requirements):
        job = Jobs()
        job.clear_volunters()
        job.assign_times(start_time, end_time)
        job.assign_date(date)
        job.assign_job_name(job_name)
        job.assign_description(job_description)
        job.assign_requirements(job_requirements)
        job.assign_volunteers_needed(volunteers_needed)
        db.session.add(job)
        db.session.commit()