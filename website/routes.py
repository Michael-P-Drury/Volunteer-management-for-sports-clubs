from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .databases import User, Jobs, Qualification, Requests
from . import lm, db, app
from .forms import removeMobile, removeEmail, mobileChangeForm, emailChangeForm, LoginForm, SignupForm, newJobForm, QualificationForm
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
        current_user_id = current_user.get_id()
        job_id_request = request.form['job_id_request']

        user = User.query.get(current_user_id)
        job = Jobs.query.get(job_id_request)

        new_request = Requests()

        new_request.user_id.append(user)
        new_request.job_id.append(job)

        db.session.add(new_request)
        db.session.commit()


    return render_template('timetable.html', jobs=jobs, current_user_id = current_user_id)


@app.route('/upload_jobs', methods=['POST'])
def upload_file():
    #Check if the file is in the request.
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    #If the user does not select a file, error.
    if file.filename == '':
        return redirect(request.url)

    if file:
        #Ensure the file is a CSV before processing.
        if file.filename.endswith('.csv'):
            #Convert the file stream to a panda
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = pd.read_csv(stream)

            #Iterate over the rows in the csv file and create new jobs intsance of each row.
            for loopcount, row in csv_input.iterrows():
                new_job = Jobs(
                    volunteers_assigned=row.get('volunteers_assigned', ''),
                    volunteers_needed=row.get('volunteers_needed', 0),
                    start_time=row.get('start_time', ''),
                    end_time=row.get('end_time', ''),
                    date=row.get('date', ''),
                    job_description=row.get('job_description', ''),
                    job_requirements=row.get('job_requirements', '')
                )
                # Add each new job to the session
                db.session.add(new_job)

            # Commit the session to save all new Jobs to the database
            db.session.commit()
            return redirect(url_for('timetable'))  # Redirect to the admin page to display jobs.
        else:
            return redirect(request.url)
    else:
        return redirect(request.url)
    

# routing for the admin page which takes you to the home page and the URL of the base URL/admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.all()
    qualifications = Qualification.query.all()
    new_job_form = newJobForm()

    requests = Requests.query.all()

    new_job_form.job_requirements.choices = [(q.qualifications_id, q.qualification_name) for q in qualifications]

    qualification_form = QualificationForm()

    if request.method == 'POST':
        try:
            out_list = request.form['accept_request']

            out_list = out_list.split(',')

            user_accept = out_list[0]
            job_accept = out_list[1]


            current_job = Jobs.query.filter_by(job_id=job_accept).first()

            current_job.add_volunteer(user_accept)

            db.session.commit()


        except:

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
                    volunteers_assigned='',
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
                           qualifications=qualifications, requests = requests)


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

    return render_template('profile.html', email_form = email_form, mobile_form = mobile_form,
                           remove_mobile = remove_mobile, remove_email = remove_email)

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


