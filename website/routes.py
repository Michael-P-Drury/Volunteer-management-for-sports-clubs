from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .databases import User, Jobs, Qualification, Requests, RemoveRequests, UserJobLink
from . import lm, db, app
from .forms import removeMobile, removeEmail, mobileChangeForm, emailChangeForm, LoginForm, SignupForm, newJobForm, QualificationForm, ProfileDetailsForm
import pandas as pd
import io

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
        if user is None or not user.verify_password(login_form.password.data):
            return redirect(url_for('login', **request.args))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=login_form)


# routing for the home page which takes you to the home page and the URL of the base URL/home
@app.route('/home')
def home():
    return render_template('home.html')


# routing for the timetable page which takes you to the home page and the URL of the base URL/timetable
@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    jobs = Jobs.query.all()
    current_user_id = current_user.get_id()

    if request.method == 'POST':
        job_id_request = request.form.get('job_id_request')
        job_request_remove = request.form.get('remove_request_job_id')

        if job_id_request:
            #handle job request
            try:
                #THIS LINE HERE IS NOT WORKING
                new_request = Requests(user_id=current_user_id, job_id=job_id_request)
                db.session.add(new_request)
                db.session.commit()
            except Exception as e:
                db.session.rollback()

        elif job_request_remove:
            #handle request to remove from a job
            try:
                new_remove_request = RemoveRequests(user_id=current_user_id, job_id=job_request_remove)
                db.session.add(new_remove_request)
                db.session.commit()
            except Exception as e:
                db.session.rollback()

        return redirect(url_for('timetable'))
    
    assigned_jobs = UserJobLink.query.filter_by(user_id=current_user_id).all()
    assigned_job_ids = {link.job_id for link in assigned_jobs}

    requested_jobs = Requests.query.filter_by(user_id=current_user_id).all()
    requested_job_ids = {req.job_id for req in requested_jobs}

    requested_removals = RemoveRequests.query.filter_by(user_id=current_user_id).all()
    requested_removal_job_ids = {rem.job_id for rem in requested_removals}

    return render_template('timetable.html', jobs=jobs, assigned_job_ids=assigned_job_ids,
                           requested_job_ids=requested_job_ids, requested_removal_job_ids=requested_removal_job_ids)



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

        expected_headers = ['volunteers_needed', 'start_time', 'end_time', 'date', 'job_description', 'job_requirements']

        if not all(header in csv_input.columns for header in expected_headers):
            return redirect(request.url)

        errors = []
        for index, row in csv_input.iterrows():
            try:
                new_job = Jobs(
                    volunteers_needed=row['volunteers_needed'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    date=row['date'],
                    job_description=row['job_description'],
                    job_requirements=row['job_requirements']
                )
                db.session.add(new_job)
            except Exception as e:
                errors.append(f"Error in row {index}: {e}")

        if errors:
            for error in errors:
                db.session.rollback()  ##rollback the session in case of errors
        else:
            db.session.commit()  #only commit if all rows are processed successfully
            return redirect(url_for('timetable'))
    else:
        return redirect(request.url)
    

# routing for the admin page which takes you to the home page and the URL of the base URL/admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.all()
    qualifications = Qualification.query.all()
    new_job_form = newJobForm()
    jobs = Jobs.query.all()

    requests = Requests.query.all()

    remove_requests = RemoveRequests.query.all()

    new_job_form.job_requirements.choices = [(q.qualifications_id, q.qualification_name) for q in qualifications]

    qualification_form = QualificationForm()

    if 'accept_request' in request.form:
            user_id, job_id = request.form['accept_request'].split(',')

            new_link = UserJobLink(user_id=user_id, job_id=job_id)
            db.session.add(new_link)

            request_to_delete = Requests.query.filter_by(user_id=user_id, job_id=job_id).first()
            if request_to_delete:
                db.session.delete(request_to_delete)
            
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
            
            remove_request_to_delete = RemoveRequests.query.filter_by(user_id=user_id, job_id=job_id).first()
            if remove_request_to_delete:
                db.session.delete(remove_request_to_delete)
                
            db.session.commit()
            return redirect(url_for('admin'))

    elif 'delete_remove_request' in request.form:
            user_id, job_id = request.form['delete_remove_request'].split(',')
            
            #find and delete the remove request without unlinking user and job
            #remove_request_to_delete = RemoveRequests.query.filter_by(user_id=user_id, job_id=job_id).first()
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
                           qualifications=qualifications, requests = requests, remove_requests = remove_requests, jobs = jobs)

@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    delete_job = Jobs.query.get(job_id)
    if delete_job:
        db.session.delete(delete_job)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_qualification/<int:qualifications_id>', methods=['POST'])
def delete_qualification(qualifications_id):
    delete_qualification = Qualification.query.get(qualifications_id)
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

        if User.query.filter_by(username=username_in).first() is None:
            User.register(username_in, password_in, admin_in)
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', form=signup_form, exists=True)

    return render_template('signup.html', form=signup_form)


# routing for the profile page which takes you to the home page and the URL of the base URL/profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():

    email_form = emailChangeForm()
    mobile_form = mobileChangeForm()

    remove_email = removeEmail()
    remove_mobile = removeMobile()

    my_requests = Requests.query.filter_by(user_id=current_user.get_id()).all()
    my_remove_requests = RemoveRequests.query.filter_by(user_id=current_user.get_id()).all()

    current_user_id = current_user.get_id()
    assigned_jobs = Jobs.query.join(UserJobLink, Jobs.job_id == UserJobLink.job_id).filter(UserJobLink.user_id == current_user_id).all()

    details_form = ProfileDetailsForm()


    if mobile_form.validate_on_submit() and mobile_form.validate():
        new_mobile = mobile_form.new_mobile.data
        for user in db.session.query(User).filter_by(user_id=current_user.get_id()):
            user.mobile = new_mobile
        db.session.commit()
        return redirect(url_for('profile'))

    if email_form.validate_on_submit() and email_form.validate():
        new_email = email_form.new_email.data
        for user in db.session.query(User).filter_by(user_id=current_user.get_id()):
            user.email = new_email
        db.session.commit()
        return redirect(url_for('profile'))

    if remove_mobile.submit4.data and remove_mobile.validate():
        for user in db.session.query(User).filter_by(user_id=current_user.get_id()):
            user.no_mobile()
        db.session.commit()
        return redirect(url_for('profile'))


    if remove_email.submit3.data and remove_email.validate():
        for user in db.session.query(User).filter_by(user_id=current_user.get_id()):
            user.no_email()
        db.session.commit()
        return redirect(url_for('profile'))
    
    if details_form.validate_on_submit():
        # Update user's profile details
        new_detail_text = details_form.detail_text.data
        for user in db.session.query(User).filter_by(user_id=current_user.get_id()):
            user.details = new_detail_text
        db.session.commit()
        return redirect(url_for('profile'))

    user_profile_details = current_user.profile_details
    qualifications = Qualification.query.all()

    if request.method == 'POST':

        selected_qualification_ids = request.form.getlist('qualification_ids')  #correctly retrieves list of selected qualification IDs
        current_user.qualifications = [Qualification.query.get(id) for id in selected_qualification_ids]
        db.session.commit()
        return redirect(url_for('profile'))
    
    return render_template('profile.html', assigned_jobs=assigned_jobs, email_form=email_form, mobile_form=mobile_form,
                           remove_mobile=remove_mobile, remove_email=remove_email, qualifications=Qualification.query.all(),
                           user_qualifications=[q.qualifications_id for q in current_user.qualifications], my_requests=my_requests,
                           my_remove_requests=my_remove_requests, details_form=details_form)

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
