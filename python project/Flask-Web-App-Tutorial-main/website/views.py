from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
from .models import User, Company_User, Job, JobApplied, JobAccepted
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import json


def send_email(sender_email, sender_password, recipient_email, subject, body):
    # Create a MIMEText object to represent the email content
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the body to the message
    message.attach(MIMEText(body, 'plain'))

    # Establish a secure SMTP connection to Gmail's server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        try:
            # Log in to your Gmail account
            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print("Error sending email:", str(e))


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def firstpage():
    session['session_valid_alumni'] = False
    session['sesston_valid_company'] = False
    return render_template("first page.html", user=current_user)


@views.route('/alumnihome', methods=['GET', 'POST'])
def alumnihome():
    if session['session_valid_alumni']:
        return render_template("alumnihome.html", user=current_user)
    else:
        flash("Login to access this page")
        return render_template("first page.html")


@views.route('/apply_job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if session['session_valid_alumni']:
        # Retrieve the job and user
        job = Job.query.get(job_id)
        user = current_user

        # Create a new job application entry
        new_application = JobApplied(job_id=job_id, user_id=user.id)
        db.session.add(new_application)
        db.session.commit()
        for job in session['jobs_available']:
            if job['id'] == job_id:
                job['applied'] = True
        flash('Application submitted successfully!', category='success')
        return redirect(url_for('views.jobsavailable'))
    return render_template('first page.html')


@views.route('/jobsavailable', methods=['GET', 'POST'])
def jobsavailable():
    if session['session_valid_alumni']:
        jobs_available = session['jobs_available']
        user = current_user
        return render_template('jobsavailable.html', user=current_user, jobs_available=jobs_available)
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/searchjob', methods=['GET', 'POST'])
def searchjob():
    if session['session_valid_alumni']:
        if request.method == 'POST':
            search_according_qualification = request.form.get('search_according_qualification')
            all_jobs = Job.query.all()
            all_companies = Company_User.query.all()
            jobs_according_to_search = []

            user_applied_jobs = []
            user = current_user
            all_job_applications = JobApplied.query.all()
            for job_application in all_job_applications:
                if job_application.user_id == user.id:
                    user_applied_jobs.append(job_application.job_id)

            i = 1
            for jobs in all_jobs:
                if jobs.qualifications_required == search_according_qualification:
                    company_name = None
                    for company in all_companies:
                        if company.id == jobs.company__user_id:
                            company_name = company.company_name
                            break
                    job_info = {
                        'sl_no': i,
                        'id': jobs.id,
                        'job_title': jobs.title,
                        'qualifications_required': jobs.qualifications_required,
                        'additional_requirements': jobs.additional_requirements,
                        'company_name': company_name,
                        'applied': jobs.id in user_applied_jobs  # Check if user has applied
                    }
                    jobs_according_to_search.append(job_info)
                    i += 1

            session['jobs_available'] = jobs_according_to_search
            return redirect(url_for('views.jobsavailable'))
        return render_template('searchjob.html', user=current_user)
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/updatejob/<int:id>', methods=['GET', 'POST'])
def updatejob(id):
    if session['session_valid_company']:
        if request.method == 'POST':
            job_to_update = Job.query.get(id)
            if request.form.get('jobtitle'):
                job_to_update.title = request.form.get('jobtitle')
            if request.form.get('qualifications_required'):
                if request.form.get('qualifications_required') != "None":
                    job_to_update.qualifications_required = request.form.get('qualifications_required')
            if request.form.get('additionalrequirments'):
                job_to_update.additional_requirements = request.form.get('additionalrequirments')
            db.session.commit()
            flash("Job Successfully updated", category='success')
        return render_template('updatejob.html', user=current_user)
    return render_template('first page.html')


@views.route('/deletejob/<int:id>', methods=['POST'])
def deletejob(id):
    if session['session_valid_company']:
        job_to_delete = Job.query.get(id)
        JobApplied.query.filter_by(job_id=id).delete()
        if job_to_delete:
            db.session.delete(job_to_delete)
        db.session.commit()
        return redirect('/viewjobs')
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/viewjobs', methods=['GET', 'POST'])
def viewjobs():
    if session['session_valid_company']:
        all_jobs = Job.query.all()
        jobs = []
        for job in all_jobs:
            if job.company__user_id == current_user.id:
                jobs.append(job)

        return render_template('viewjobs.html', user=current_user, all_jobs=jobs)
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/accept_application/<int:job_id>/<int:user_id>', methods=['POST'])
def accept_application(job_id, user_id):
    if session['session_valid_company']:
        new_entry = JobAccepted(job_id=job_id, user_id=user_id)
        db.session.add(new_entry)
        user = User.query.get(user_id)
        user_email = user.email
        job_to_delete = Job.query.get(job_id)
        print(job_to_delete)
        sender_email = "thegreatmanbhargav@gmail.com"
        sender_password = "hedjojqqxanjwvup"
        recipient_email = user_email
        subject = "Job Acceptance"
        body = "Your job application for Job details: Job Title-" + job_to_delete.title + "\n Qualification-" + job_to_delete.qualifications_required + "\n Additional requirments-" + job_to_delete.additional_requirements + "\nCompany Name-" +session['company_user'].company_name + "\nHas been Accepted. For further details contact: " + session['company_user'].email

        if job_to_delete:
            JobApplied.query.filter_by(job_id=job_id).delete()
            db.session.delete(job_to_delete)
        db.session.commit()
        send_email(sender_email, sender_password, recipient_email, subject, body)

        return redirect('/jobapplications')
    flash('Login to access this page')
    render_template('first page.html')

@views.route('/reject_application/<int:job_id>/<int:user_id>', methods=['POST'])
def reject_application(job_id, user_id):
    if session['session_valid_company']:
        application_to_delete = JobApplied.query.filter_by(job_id=job_id, user_id=user_id).first()
        if application_to_delete:
            db.session.delete(application_to_delete)
            db.session.commit()
        return redirect('/jobapplications')
    flash('Login to access this page')
    return render_template('first page.html')



@views.route('/jobapplications', methods=['POST', 'GET'])
def jobapplications():
    if session['session_valid_company']:
        user = session['company_user']
        jobs_with_applications = []

        all_company_jobs = Job.query.filter_by(company__user_id=user.id)
        for job in all_company_jobs:
            applications = []
            job_applied = JobApplied.query.filter_by(job_id=job.id)
            for entry in job_applied:
                user = User.query.get(entry.user_id)
                if user:
                    application_data = {
                        'user_name': user.first_name,
                        'job_id': job.id,
                        'user_id': user.id,
                        'resume': user.resume_link
                    }
                    applications.append(application_data)
            jobs_with_applications.append({
                'job': job,
                'applications': applications
            })
        return render_template('jobapplications.html', user=current_user, jobs_with_applications=jobs_with_applications)
    flash('Login to access this page')
    return render_template('first page.html')

@views.route('/addjob', methods=['POST', 'GET'])
def addjob():
    if session['session_valid_company']:
        if request.method == 'POST':
            job_title = request.form.get('jobtitle')
            qualifications_required = request.form.get('qualifications_required')
            print(qualifications_required)
            job_additional_requirments = request.form.get('additionalrequirments')
            company_id = session['id']
            new_job = Job(title=job_title, qualifications_required=qualifications_required,
                      additional_requirements=job_additional_requirments, company__user_id=company_id)
            db.session.add(new_job)
            db.session.commit()
            flash('Job was added successfully', category='success')
            return redirect('/addjob')
        return render_template("addjob.html", user=current_user)
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/appliedjobs', methods=['GET'])
def appliedjobs():
    if session['session_valid_alumni']:
        user = session['user']
        applications = JobApplied.query.all()
        jobs = []
        i = 1
        for application in applications:
            if application.user_id == user.id:
                job = Job.query.get(application.job_id)
                company_name = (Company_User.query.get(job.company__user_id)).company_name
                job_info = {
                    'sl_no': i,
                    'job_id': application.job_id,
                    'job_title': job.title,
                    'qualification_required': job.qualifications_required,
                    'additional_requirments': job.additional_requirements,
                    'company_name': company_name
                }
                jobs.append(job_info)
        print(jobs)
        return render_template("appliedjobs.html", user=current_user, jobs_available=jobs)
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/companyhome', methods=['GET', 'POST'])
def companyhome():
    if session['session_valid_company']:
        return render_template("companyhome.html", user=current_user)
    flash("Login to access this page")
    return render_template('first page.html')


@views.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    if session['session_valid_alumni']:
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            age = int(request.form.get('age'))
            contactno = request.form.get('contactno')
            year_of_graduation = request.form.get('year_of_graduation')
            department = request.form.get('department')
            USN = request.form.get('USN')
            resume_link = request.form.get('resume_link')
            if age < 0 or age > 150:
                flash('Invalid age entered', 'error')
                return redirect(request.url)

            if not contactno.isdigit() or len(contactno) > 20:
                flash('Invalid contact number', 'error')
                return redirect(request.url)

            if not year_of_graduation.isdigit() or len(year_of_graduation) != 4:
                flash('Invalid year of graduation', 'error')
                return redirect(request.url)

            if not department or len(department) > 100:
                flash('Invalid department', 'error')
                return redirect(request.url)

            if not USN or len(USN) > 15:
                flash('Invalid USN', 'error')
                return redirect(request.url)

            user = session['user']
            user.first_name = full_name
            user.age = age
            user.login_first = 0
            user.contactno = contactno
            user.year_of_graduation = year_of_graduation
            user.department = department
            user.USN = USN
            user.resume_link = resume_link
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('views.viewprofile'))
        user = session['user']
        return render_template("updateprofile.html", user=user)
    flash('Login to access to this page')
    return render_template('first page.html')


@views.route('/resetpassword1', methods=['GET', 'POST'])
def resetpassword1():
    if session['session_valid_alumni']:

        if request.method == 'POST':
            previous_password = request.form.get('password1')
            new_password = request.form.get('password2')
            reenter_new_password = request.form.get('password3')

            user = session['user']

            if check_password_hash(user.password, previous_password):
                if new_password == reenter_new_password:
                    if len(new_password) >= 7:  # Check if the new password meets the length requirement
                        user.password = generate_password_hash(new_password, method="sha256")
                        db.session.commit()
                        flash('Password has been reset successfully.', category='success')
                        return redirect(url_for('views.resetpassword1'))
                    else:
                        flash('Password must be at least 7 characters.', category='error')
                else:
                    flash('New passwords do not match.', category='error')
            else:
                flash('Incorrect previous password.', category='error')

        return render_template('resetpassword1.html', user=current_user)
    flash('Login to access this page')
    return render_template('first page.html')


@views.route('/viewprofile')
def viewprofile():
    if session['session_valid_alumni']:
        email = session['email']
        user = User.query.filter_by(email=email).first()
        return render_template("viewprofile.html", user=user)
    flash('Login to access this page')
    return render_template('first page.html')
