from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

#A many-to-many table for linking users and their qualifications.
UserQualifications = db.Table('UserQualifications',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('qualification_id', db.Integer, db.ForeignKey('qualification.qualifications_id'), primary_key=True)
)

#A many-to-many table for linking jobs and their qualifications.
JobRequirements = db.Table('JobRequirements',
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.job_id'), primary_key=True),
    db.Column('qualification_id', db.Integer, db.ForeignKey('qualification.qualifications_id'), primary_key=True)
)

#Table to link users and jobs directly which is used for managing job assignments.
class UserJobLink(db.Model):
    __tablename__ = 'user_job_link'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), primary_key=True)


#A user Table defining attributes for user information and relationships with the other models.
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(30))
    mobile = db.Column(db.String(15))
    dob = db.Column(db.String(11))
    address = db.Column(db.String(50))
    jobs_completed = db.Column(db.Integer)
    admin = db.Column(db.Boolean)
    details = db.Column(db.String(255))
    qualifications = db.relationship('Qualification', secondary=UserQualifications,
                                     backref=db.backref('users', lazy='subquery'))
    jobs = db.relationship('Jobs', secondary='user_job_link',
                           backref=db.backref('assigned_users', lazy='dynamic'))

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
    
    # sets the details inputted
    def set_details(self, details):
        self.details = details
        print("test")

    # sets admin statas as inputted
    def set_admin(self, admin):
        self.admin = admin

    # sets mobile number to blank
    def no_mobile(self):
        self.mobile = None

    # sets qualifications to blank
    def no_qualifications(self):
        self.qualifications = []

    # sets the users events to blank
    def no_events(self):
        self.events = None

    def no_jobs_completed(self):
        self.jobs_completed = 0

    # sets email to blank
    def no_email(self):
        self.email = None

    def no_dob(self):
        self.dob = None
    
    def no_address(self):
        self.address = None

    #sets details to blank
    def no_details(self):
        self.details = None

    def increase_jobs(self):
        new_amount_jobs = self.jobs_completed + 1

        self.jobs_completed = new_amount_jobs

    def decrease_jobs(self):
        new_amount_jobs = self.jobs_completed - 1

        self.jobs_completed = new_amount_jobs

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
        user.no_details()
        user.no_jobs_completed()
        db.session.add(user)
        db.session.commit()
        return user

    # needed for getting users
    def __repr__(self):
        return '<User {0}>'.format(self.username)


# creates the job table which stores all the jobs

# stores date as a string in the format 'day/month/year'
# stores time as a string in the format 'hour:minute'

class Jobs(UserMixin, db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(20))
    volunteers_needed = db.Column(db.Integer)
    volunteers_needed_left = db.Column(db.Integer)
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    date = db.Column(db.String(20))
    job_description = db.Column(db.String(300))

    job_qualifications = db.relationship('Qualification', secondary=JobRequirements,
                                         backref=db.backref('required_for_jobs', lazy='subquery'))

    def clear_volunteers(self):
        links = UserJobLink.query.filter_by(job_id=self.job_id).all()
        for link in links:
            db.session.delete(link)
        db.session.commit()

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
    def assign_requirements(self, JobRequirements):
        self.JobRequirements = JobRequirements

    # assigns the number of volunteers needed to a job
    def assign_volunteers_needed(self, volunteers_needed):
        self.volunteers_needed = volunteers_needed

    def assign_volunteers_needed_left(self, volunteers_needed):
        self.volunteers_needed_left = volunteers_needed

    # assigns job name to the job
    def assign_job_name(self, new_job_name):
        self.job_name = new_job_name

    def add_volunteer(self, user_id):

        new_link = UserJobLink(user_id=user_id, job_id=self.job_id)
        db.session.add(new_link)

        db.session.commit()

    def remove_volunteer(self, user_id):

        link = UserJobLink.query.filter_by(user_id=user_id, job_id=self.job_id).first()
        if link:
            db.session.delete(link)
            db.session.commit()

    def increase_needed_left(self):
        self.volunteers_needed_left += 1

    def decrease_needed_left(self):
        self.volunteers_needed_left -= 1

    # creates a new job with the information passed into it
    @staticmethod
    def add_new_job(job_name, volunteers_needed, start_time, end_time, date, job_description, JobRequirements):
        job = Jobs()
        job.clear_volunters()
        job.assign_times(start_time, end_time)
        job.assign_date(date)
        job.assign_job_name(job_name)
        job.assign_description(job_description)
        job.assign_requirements(JobRequirements)
        job.assign_volunteers_needed(volunteers_needed)
        job.assign_volunteers_needed_left(volunteers_needed)
        db.session.add(job)
        db.session.commit()

#Table for qualifications that users can possess and jobs that may require.
class Qualification(UserMixin, db.Model):
    __tablename__ = 'qualification'
    qualifications_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qualification_name = db.Column(db.String(300))
    qualification_description = db.Column(db.String(300))

#Table for handling annoucements in the systems.
class Announcements(UserMixin, db.Model):
    __tablename__ = 'announcements'
    announcement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    announcement_name = db.Column(db.String(40))
    announcement_text = db.Column(db.String(1000))

#Table for managing requests related to qualifications, linking the users and qualifications.
class QualificationRequests(UserMixin, db.Model):
    __tablename__ = 'qualification_requests'
    qualification_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    qualification_id = db.Column(db.Integer, db.ForeignKey('qualification.qualifications_id'))

    user = db.relationship('User', backref=db.backref('requests', lazy='subquery'))
    qualification = db.relationship('Qualification', backref=db.backref('requests', lazy='subquery'))

#Table for handling requests in the system.
class Requests(UserMixin, db.Model):
    __tablename__ = 'requests'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'))

    user = db.relationship('User', backref=db.backref('users', lazy='subquery'))
    job = db.relationship('Jobs', backref=db.backref('jobs', lazy='subquery'))

#Table for handling remove requests.
class RemoveRequests(UserMixin, db.Model):
    __tablename__ = 'remove_requests'
    remove_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'))

    user = db.relationship('User', backref=db.backref('remove_requests', lazy='subquery'))
    job = db.relationship('Jobs', backref=db.backref('remove_requests', lazy='subquery'))