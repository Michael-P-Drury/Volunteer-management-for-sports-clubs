from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .databases import User, Jobs, Qualification, Requests, RemoveRequests, UserJobLink, QualificationRequests, Announcements
from . import lm, db, app, admin_key, prescription_level
from .forms import LoginForm, profileEditForm, SignupForm, newJobForm, QualificationForm, ProfileDetailsForm, AnouncmentForm
import pandas as pd
import io
from sqlalchemy import desc

# from .forms import ... (if you want to import a form)
# routing for the pages in the website


# route for the login page
# the login page is the first page and so its URL is just blank
@app.route('/', methods=['GET', 'POST'])
def login():
    # form is the variable for the logins form
    login_form = LoginForm()


    # if the form is submitted the checks if user is in database and checks password
    # if user is verified takes to home page and log ins the current user as the current user
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()

        if user is None:
            return render_template('login.html', form=login_form, error = 'invalid username')

        if not user.verify_password(login_form.password.data):
            return render_template('login.html', form=login_form, error = 'invalid password')

        login_user(user)

        return redirect(url_for('current_jobs'))
    return render_template('login.html', form=login_form)


# routing for the home page which takes you to the home page and the URL of the base URL/home
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/my_jobs', methods=['GET', 'POST'])
def my_jobs():

    current_user_id = current_user.get_id()
    
    assigned_jobs = Jobs.query.join(UserJobLink, Jobs.job_id == UserJobLink.job_id).filter(UserJobLink.user_id == current_user_id).all()
    
    my_remove_requests = RemoveRequests.query.filter_by(user_id=current_user_id).all()
    requested_removal_job_ids = [rem.job_id for rem in my_remove_requests]
    
    assigned_job_ids = []
    for assigned_job in assigned_jobs:
        assigned_job_ids.append(assigned_job.job_id)

    requested_job_ids = []
    requested_jobs = Requests.query.filter_by(user_id=current_user_id).all()
    for requested in requested_jobs:
        requested_job_ids.append(requested.job_id)

    if 'remove_request_job_id' in request.form:
        job_id_request = request.form['remove_request_job_id']
        new_request = RemoveRequests(user_id=current_user_id, job_id=job_id_request)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('my_jobs'))
    
    return render_template('my_jobs.html',assigned_jobs=assigned_jobs, assigned_job_ids=assigned_job_ids, requested_job_ids=requested_job_ids,
                           my_remove_requests=my_remove_requests, requested_removal_job_ids=requested_removal_job_ids,
                           current_user_id=current_user_id, job_table=Jobs, prescription_level = prescription_level)

# routing for the current jobs page which takes you to the home page and the URL of the base URL/current_jobs
@app.route('/current_jobs', methods=['GET', 'POST'])
def current_jobs():

    jobs = Jobs.query.all()
    current_user_id = current_user.get_id()
    user = User.query.get(current_user_id)

    user_qualifications_ids = {q.qualifications_id for q in user.qualifications}

    qualified_jobs_ids = []

    for job in jobs:
        job_requirement_ids = {qr.qualifications_id for qr in job.job_qualifications}
        if job_requirement_ids.issubset(user_qualifications_ids):
            qualified_jobs_ids.append(job.job_id)

    assigned_job_ids = []
    assigned_jobs = UserJobLink.query.filter_by(user_id=current_user_id).all()
    for assigned_job in assigned_jobs:
        assigned_job_ids.append(assigned_job.job_id)

    requested_job_ids = []
    requested_jobs = Requests.query.filter_by(user_id=current_user_id).all()
    for requested in requested_jobs:
        requested_job_ids.append(requested.job_id)

    if 'job_id_request' in request.form:
        job_id_request = request.form['job_id_request']
        new_request = Requests(user_id=current_user_id, job_id=job_id_request)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('current_jobs'))

    return render_template('current_jobs.html', jobs=jobs, qualified_jobs_ids=qualified_jobs_ids,
                           requested_job_ids=requested_job_ids, assigned_job_ids=assigned_job_ids, prescription_level = prescription_level)


@app.route('/upload_jobs', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = pd.read_csv(stream)
        
        expected_headers = ['job_name', 'volunteers_needed', 'start_time', 'end_time', 'date', 'job_description', 'qualifications']

        if not all(header in csv_input.columns for header in expected_headers):
            return redirect(request.url)

        errors = []
        for index, row in csv_input.iterrows():
            try:
                qualifications_list = row['qualifications'].split(';')
                qualification_objects = Qualification.query.filter(Qualification.qualification_name.in_(qualifications_list)).all()

                new_job = Jobs(
                    job_name=row['job_name'],
                    volunteers_needed=row['volunteers_needed'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    date=row['date'],
                    job_description=row['job_description'],
                    job_qualifications=qualification_objects
                )
                db.session.add(new_job)

            except Exception as e:
                errors.append(f"Error in row {index}: {e}")

        if errors:
            for error in errors:
                db.session.rollback()  ##rollback the session in case of errors
        else:
            db.session.commit()  #only commit if all rows are processed successfully
            return redirect(url_for('current_jobs'))
    else:
        return redirect(request.url)
    

# routing for the admin page which takes you to the home page and the URL of the base URL/admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.order_by(desc(User.jobs_completed)).all()
    qualifications = Qualification.query.all()
    new_job_form = newJobForm()
    jobs = Jobs.query.all()
    user_job_link = UserJobLink.query.all()

    requests = Requests.query.join(User).order_by(User.jobs_completed).all()

    qualification_requests = QualificationRequests.query.join(User).all()

    remove_requests = RemoveRequests.query.join(User).order_by(User.jobs_completed).all()

    new_job_form.job_requirements.choices = [(q.qualifications_id, q.qualification_name) for q in qualifications]

    qualification_form = QualificationForm()

    if 'accept_request' in request.form:
            user_id, job_id = request.form['accept_request'].split(',')

            new_link = UserJobLink(user_id=user_id, job_id=job_id)
            db.session.add(new_link)

            job = Jobs.query.filter_by(job_id=job_id).first()
            job.decrease_needed_left()

            request_to_delete = Requests.query.filter_by(user_id=user_id, job_id=job_id).first()
            if request_to_delete:
                db.session.delete(request_to_delete)
            
            db.session.commit()
            return redirect(url_for('admin'))

    elif 'accept_qualification_request' in request.form:
        user_id, qualification_id = request.form['accept_qualification_request'].split(',')

        user = User.query.filter_by(user_id = user_id).first()

        new_qualification = Qualification.query.filter_by(qualifications_id = qualification_id).first()

        user.qualifications.append(new_qualification)

        request_to_delete = QualificationRequests.query.filter_by(user_id=user_id, qualification_id=qualification_id).first()

        if request_to_delete:
            db.session.delete(request_to_delete)

        db.session.commit()

        return redirect(url_for('admin'))

    elif 'add_admin_user_id' in request.form:

        user_id = request.form['add_admin_user_id']

        user = User.query.filter_by(user_id = user_id).first()

        user.set_admin(True)

        db.session.commit()

        return redirect(url_for('admin'))

    elif 'delete_qualification_request' in request.form:
        user_id, qualification_id = request.form['delete_qualification_request'].split(',')

        request_to_delete = QualificationRequests.query.filter_by(user_id=user_id, qualification_id=qualification_id).first()

        if request_to_delete:
            db.session.delete(request_to_delete)

        db.session.commit()

        return redirect(url_for('admin'))

    elif 'remove_volunteer' in request.form:

        user_id, job_id = request.form['remove_volunteer'].split(',')

        link_to_delete = UserJobLink.query.filter_by(user_id=user_id, job_id=job_id).first()
        if link_to_delete:
            db.session.delete(link_to_delete)

        job = Jobs.query.filter_by(job_id=job_id).first()
        job.increase_needed_left()

        db.session.commit()
        return redirect(url_for('admin'))


    elif 'increase_user_id' in request.form:

        user_id = request.form['increase_user_id']

        user = User.query.filter_by(user_id = user_id).first()

        user.increase_jobs()

        db.session.commit()

        return redirect(url_for('admin'))

    elif 'auto_assign_job_id' in request.form:

        job_id = request.form['auto_assign_job_id']

        volunteers = User.query.order_by(User.jobs_completed).all()

        job = Jobs.query.filter_by(job_id = job_id).first()

        needed_left = job.volunteers_needed_left

        i = 0

        while needed_left > 0:
            try:
                current_volunteer = volunteers[i]
                assigned_jobs = Jobs.query.join(UserJobLink, Jobs.job_id == UserJobLink.job_id).filter(UserJobLink.user_id == current_volunteer.user_id).all()

                assigned_job_ids = []
                for assigned_job in assigned_jobs:
                    assigned_job_ids.append(assigned_job.job_id)

                user_qualifications_ids = {q.qualifications_id for q in current_volunteer.qualifications}

                qualified_jobs_ids = []

                for loopjob in jobs:
                    job_requirement_ids = {qr.qualifications_id for qr in loopjob.job_qualifications}
                    if job_requirement_ids.issubset(user_qualifications_ids):
                        qualified_jobs_ids.append(loopjob.job_id)

                if job.job_id not in assigned_job_ids and job.job_id in qualified_jobs_ids:

                    new_link = UserJobLink(user_id=current_volunteer.user_id, job_id=job_id)
                    db.session.add(new_link)

                    job.decrease_needed_left()

                    db.session.commit()

                    needed_left = needed_left - 1

                i = i + 1

            except:
                needed_left = 0

        return redirect(url_for('admin'))


    elif 'decrease_user_id' in request.form:

        user_id = request.form['decrease_user_id']

        user = User.query.filter_by(user_id=user_id).first()

        user.decrease_jobs()

        db.session.commit()

        return redirect(url_for('admin'))

    elif 'delete_request' in request.form:
            user_id, job_id = request.form['delete_request'].split(',')

            request_to_delete = Requests.query.filter_by(user_id=user_id, job_id=job_id).first()
            if request_to_delete:
                db.session.delete(request_to_delete)
            
            db.session.commit()
            return redirect(url_for('admin'))

    elif 'accept_remove_request' in request.form:
            user_id, job_id = request.form['accept_remove_request'].split(',')
 
            link_to_delete = UserJobLink.query.filter_by(user_id=user_id, job_id=job_id).first()
            if link_to_delete:
                db.session.delete(link_to_delete)

            job = Jobs.query.filter_by(job_id = job_id).first()
            job.increase_needed_left()

            remove_request_to_delete = RemoveRequests.query.filter_by(user_id=user_id, job_id=job_id).first()
            if remove_request_to_delete:
                db.session.delete(remove_request_to_delete)
                
            db.session.commit()
            return redirect(url_for('admin'))

    elif 'delete_remove_request' in request.form:
            user_id, job_id = request.form['delete_remove_request'].split(',')

            remove_request_to_delete = RemoveRequests.query.filter_by(user_id=int(user_id), job_id=int(job_id)).first()
            if remove_request_to_delete:
                db.session.delete(remove_request_to_delete)
            
            db.session.commit()
            return redirect(url_for('admin'))

    if new_job_form.validate_on_submit():

        new_job_name = new_job_form.job_name.data
        new_job_date = new_job_form.date.data
        new_job_start = new_job_form.start_time.data
        new_job_end = new_job_form.end_time.data
        # new_job_requirements = new_job_form.job_requirements.data
        selected_qualifications = new_job_form.job_requirements.data #NEW
        new_job_volunteers_needed = new_job_form.volunteers_needed.data
        new_job_description = new_job_form.job_description.data

        new_job_start_hour = new_job_start.hour
        new_job_start_minute = new_job_start.minute

        new_job_end_hour = new_job_end.hour
        new_job_end_minute = new_job_end.minute

        new_job_year = new_job_date.year
        new_job_month = new_job_date.month
        new_job_day = new_job_date.day

        date_insert = f'{new_job_day}/{new_job_month}/{new_job_year}'
        start_time_insert = f'{new_job_start_hour}:{new_job_start_minute}'
        end_time_insert = f'{new_job_end_hour}:{new_job_end_minute}'


        new_job = Jobs(
            #volunteers_assigned='',
            volunteers_needed=new_job_volunteers_needed,
            volunteers_needed_left = new_job_volunteers_needed,
            start_time=start_time_insert,
            end_time=end_time_insert,
            date=date_insert,
            job_description=new_job_description,
            #job_requirements='',
            job_name = new_job_name
        )

        db.session.add(new_job)
        db.session.flush()

        for qual_id in selected_qualifications:
            qualification = Qualification.query.get(qual_id)
            new_job.job_qualifications.append(qualification)

        db.session.commit()

        return redirect(url_for('admin'))

    if qualification_form.validate_on_submit():
        new_qualification = Qualification(
            qualification_name=qualification_form.qualification_name.data,
            qualification_description=qualification_form.qualification_description.data,
        )

        db.session.add(new_qualification)
        db.session.commit()

        return redirect(url_for('admin'))


    return render_template('admin.html', users=users, new_job_form=new_job_form, qualification_form=qualification_form,
                           qualifications=qualifications, requests = requests, remove_requests = remove_requests,
                           jobs = jobs, user_job_link = user_job_link, all_users = User,
                           prescription_level = prescription_level, qualification_requests = qualification_requests)

@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    delete_job = Jobs.query.get(job_id)

    if delete_job:

        remove_requests_to_delete = RemoveRequests.query.filter_by(job_id=int(job_id)).all()

        for remove_request_to_delete in remove_requests_to_delete:
            db.session.delete(remove_request_to_delete)

        requests_to_delete = Requests.query.filter_by(job_id=int(job_id)).all()
        for request_to_delete in requests_to_delete:
            db.session.delete(request_to_delete)

        db.session.delete(delete_job)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_qualification/<int:qualifications_id>', methods=['POST'])
def delete_qualification(qualifications_id):
    delete_qualification = Qualification.query.get(qualifications_id)

    delete_requests = QualificationRequests.query.filter_by(qualification_id = qualifications_id).all()
    for delete_request in delete_requests:
        db.session.delete(delete_request)
        db.session.commit()

    if delete_qualification:
        db.session.delete(delete_qualification)
        db.session.commit()
    return redirect(url_for('admin'))

# route for the signup page which takes you to the home page and the URL of the base URL/signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # signup_form is the variable for the logins form
    signup_form = SignupForm()

    # if form is submitted then creates a new user adding the submitted details to the database and takes user to login
    if signup_form.validate_on_submit():

        password_in = str(signup_form.password.data)
        username_in = str(signup_form.username.data)
        admin_in = bool(signup_form.admin.data)
        admin_key_in = str(signup_form.admin_key.data)
        age_c_in = bool(signup_form.age_confirm.data)

        if age_c_in:
            if User.query.filter_by(username=username_in).first() is None:
                if admin_in and admin_key_in == admin_key:
                    User.register(username_in, password_in, admin_in)
                    return redirect(url_for('login'))
                elif not admin_in:
                    User.register(username_in, password_in, admin_in)
                    return redirect(url_for('login'))
                else:
                    return render_template('signup.html', form=signup_form, error_text = True)
            else:
                return render_template('signup.html', form=signup_form, exists=True)
        else:
            return render_template('signup.html', form=signup_form, age_error=True)

    return render_template('signup.html', form=signup_form)


# routing for the profile page which takes you to the home page and the URL of the base URL/profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():

    user = db.session.query(User).filter_by(user_id=current_user.get_id()).first()
    profile_form = profileEditForm()

    my_requests = Requests.query.filter_by(user_id=current_user.get_id()).all()
    my_remove_requests = RemoveRequests.query.filter_by(user_id=current_user.get_id()).all()
    job_table = Jobs

    current_user_id = current_user.get_id()
    assigned_jobs = Jobs.query.join(UserJobLink, Jobs.job_id == UserJobLink.job_id).filter(UserJobLink.user_id == current_user_id).all()

    details_form = ProfileDetailsForm()

    all_qualifications = Qualification.query.all()

    qualifications = []

    user_qualification_ids = []

    user_qualifications = user.qualifications

    for qualification in user_qualifications:
        user_qualification_ids.append(qualification.qualifications_id)

    for qualification in all_qualifications:
        if not qualification.qualifications_id in user_qualification_ids:
            qualifications.append(qualification)

    if request.method == 'POST':
        try:
            # Runs code for the profile form
            if request.form['form_name'] == 'profileEditForm':
                if profile_form.save_changes.data and profile_form.validate_on_submit():
                    print('Changes saved and form validated')
                    new_mobile = profile_form.new_mobile.data
                    new_email = profile_form.new_email.data
                    new_dob = profile_form.new_dob.data
                    new_address = profile_form.new_address.data
                    new_gender = profile_form.new_gender.data
                    if new_mobile : user.mobile = new_mobile
                    if new_email: user.email = new_email
                    if new_dob: user.dob = new_dob
                    if new_address: user.address = new_address
                    if new_gender: user.gender = new_gender
                    db.session.commit()
                    return redirect(url_for('profile'))
                else:
                    print('Form did not validate')
                    print(profile_form.errors)

                if profile_form.remove_mobile.data:
                    user.mobile = None
                    db.session.commit()
                    return redirect(url_for('profile'))
                if profile_form.remove_email.data:
                    user.email = None
                    db.session.commit()
                    return redirect(url_for('profile'))
                if profile_form.remove_dob.data:
                    user.dob = None
                    db.session.commit()
                    return redirect(url_for('profile'))
                if profile_form.remove_address.data:
                    user.address = None
                    db.session.commit()
                    return redirect(url_for('profile'))
                if profile_form.remove_gender.data:
                    user.gender = None
                    db.session.commit()
                    return redirect(url_for('profile'))

            # Runs the code for the details form
            elif request.form['form_name'] == 'ProfileDetailsForm':
                if details_form.submit5.data:
                    # Update user's profile details
                    new_details = details_form.new_details.data
                    for user in db.session.query(User).filter_by(user_id=current_user.get_id()):
                        user.details = new_details
                    db.session.commit()
                    return redirect(url_for('profile'))


        except:

            if 'qualification_ids' in request.form:
                selected_qualification_ids = request.form.getlist('qualification_ids')
                # current_user.qualifications = [Qualification.query.get(int(id)) for id in selected_qualification_ids]
                # db.session.commit()
                for qualification_id in selected_qualification_ids:
                    new_qualification_request = QualificationRequests(user_id=current_user_id, qualification_id =qualification_id)
                    db.session.add(new_qualification_request)
                db.session.commit()

            else:
                remove_qualification_id = request.form['remove_qualification']

                old_qualifications = current_user.qualifications

                new_qualifications = []

                for old_qualification in old_qualifications:

                    if not old_qualification.qualifications_id == int(remove_qualification_id):

                        new_qualifications.append(old_qualification)


                current_user.qualifications = new_qualifications

                db.session.commit()

                return redirect(url_for('profile'))

            return redirect(url_for('profile'))
    
    return render_template('profile.html', assigned_jobs=assigned_jobs, profile_form=profile_form, qualifications=qualifications,
                           user_qualifications=[q.qualifications_id for q in current_user.qualifications], my_requests=my_requests,
                           my_remove_requests=my_remove_requests, details_form=details_form, job_table=job_table,
                           prescription_level = prescription_level)

                        # email_form=email_form, mobile_form=mobile_form,
                        # remove_mobile=remove_mobile, remove_email=remove_email
                        # dob_form=dob_form, address_form=address_form,
                        # gender_form=gender_form, remove_dob=remove_dob, 
                        # remove_address=remove_address, remove_gender=remove_gender

# routing for the announcements page which takes you to the home page and the URL of the base URL/announcements
@app.route('/announcements', methods=['GET', 'POST'])
def announcements():
    all_announcements = Announcements.query.all()
    new_announcement_form = AnouncmentForm()

    if request.method == 'POST':

        if 'announcement_id_delete' in request.form:

            id_delete = request.form['announcement_id_delete']

            to_delete = Announcements.query.filter_by(announcement_id=id_delete).first()

            if to_delete:
                db.session.delete(to_delete)

            db.session.commit()

            return redirect(url_for('announcements'))

        elif new_announcement_form.validate_on_submit():

            new_ann_name = new_announcement_form.announcement_name.data
            new_ann_text = new_announcement_form.announcement_text.data

            new_announcement = Announcements(announcement_name = new_ann_name, announcement_text = new_ann_text)

            db.session.add(new_announcement)
            db.session.commit()

            return redirect(url_for('announcements'))


    return render_template('announcements.html', announcements = all_announcements, form = new_announcement_form,
                           current_user = current_user, prescription_level = prescription_level)

# routing for the privacy page which takes you to the home page and the URL of the base URL/privacy
@app.route('/privacy')
def privacy():
    return render_template('privacypolicy.html')

# routing for the terms page which takes you to the home page and the URL of the base URL/terms
@app.route('/terms')
def terms():
    return render_template('terms.html')

# routing for the logout which takes you to the login page and logs our the current user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# is needed when working with users
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))