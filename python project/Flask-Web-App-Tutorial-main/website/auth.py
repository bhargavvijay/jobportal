from flask import Blueprint, session, render_template, request, flash, redirect, url_for
from .models import User, Company_User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random


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


auth = Blueprint('auth', __name__)


@auth.route('/companylogin', methods=['GET', 'POST'])
def companylogin():
    session['session_type'] = "company"
    if request.method == 'POST':
        session['session_type'] = "company"
        email = request.form.get('email')
        password = request.form.get('password')

        user = Company_User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user)
                session['id'] = user.id
                session['company_user'] = user
                session['session_valid_company']=True
                return redirect(url_for('views.companyhome'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("companylogin.html", user=current_user)


@auth.route('/additionaldetails', methods=['GET', 'POST'])
 
def additionaldetails():
    if session['session_valid_alumni']:
        if request.method == 'POST':
            email = session.get('email')
            age = int(request.form.get('age'))
            contactno = request.form.get('contactno')
            year_of_graduation = request.form.get('year_of_graduation')
            department = request.form.get('department')
            USN = request.form.get('USN')
            resume_link = request.form.get('resume_link')

        # Validate the entries
            if age < 0 or age > 150:
                flash('Invalid age entered', 'error')
                return redirect(request.url)  # Redirect back to the form

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

        # Update user details in the database
            user = User.query.filter_by(email=email).first()
            user.age = age
            user.login_first = 0
            user.contactno = contactno
            user.year_of_graduation = year_of_graduation
            user.department = department
            user.USN = USN
            user.resume_link = resume_link
            db.session.commit()

            flash('Details updated successfully', 'success')
            return redirect(url_for('views.alumnihome'))
        return render_template("additionaldetails.html", user=current_user)
    else:
        flash('Login To access this page')
        return render_template("first page.html", user=current_user)




@auth.route('/alumnilogin', methods=['GET', 'POST'])
def alumnilogin():
    session['session_type'] = "alumni"
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                session['email'] = email
                session['user']=user
                session['user_valid'] = True
                session['session_valid_alumni']=True
                if user.login_first == 1:
                    return redirect(url_for('auth.additionaldetails'))
                else:
                    flash('Logged in successfully!', category='success')
                return redirect(url_for('views.alumnihome'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("alumnilogin.html", user=current_user)


@auth.route('/logout', methods=['GET'])
 
def logout():
    logout_user()
    session['session_valid_alumni'] = False
    session['session_valid_company'] = False
    return redirect('/')


@auth.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    a = None
    if session['session_type'] == "alumni":
        a = 0
    elif session['session_type'] == "company":
        a = 1
    if request.method == 'POST':
        email = session.get('reset_email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1 != password2:
            flash("Passwords dont match", category='error')
        else:
            if len(password1) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                flash('password has been reseted')
                if session['session_type'] == 'alumni':
                    user = User.query.filter_by(email=email).first()
                else:
                    user = Company_User.query.filter_by(email=email).first()
                print(user.password)
                user.password = generate_password_hash(password1, method='sha256')
                print(user.password)
                db.session.commit()
                if a == 1:
                    return redirect(url_for('auth.companylogin'))
                elif a == 0:
                    return redirect(url_for('auth.alumnilogin'))

    return render_template("resetpassword.html", user=current_user, a=a)


@auth.route('/emailverification', methods=['GET', 'Post'])
def emailverification():
    a = None
    if session['session_type'] == "alumni":
        a = 0
    elif session['session_type'] == "company":
        a = 1
    if request.method == 'POST':
        code1 = int(request.form.get('code'))
        code = session.get('verification_code')
        if code != code1:
            flash("Verification code is wrong", category='error')
        else:
            return redirect(url_for('auth.resetpassword'))

    return render_template("emailverification.html", user=current_user, a=a)


@auth.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    a = None
    if session['session_type'] == "alumni":
        a = 0
    elif session['session_type'] == "company":
        a = 1
    if request.method == 'POST':

        user = None

        email = request.form.get('email')
        if session['session_type'] == "alumni":
            user = User.query.filter_by(email=email).first()

        elif session['session_type'] == "company":
            user = Company_User.query.filter_by(email=email).first()

        if user:
            code = random.randint(100000, 999999)
            session['verification_code'] = code
            session['reset_email'] = email
            sender_email = "thegreatmanbhargav@gmail.com"
            sender_password = "hedjojqqxanjwvup"
            recipient_email = email
            subject = "Email verification"
            body = "The email verification code is:" + str(code)

            send_email(sender_email, sender_password, recipient_email, subject, body)
            return redirect(url_for('auth.emailverification'))

        else:
            flash('Email does not exist!', category='error')

    return render_template("forgotpassword.html", user=current_user, a=a)


@auth.route('/emailverification1', methods=['GET', 'Post'])
def emailverification1():
    a = None
    if session['session_type'] == "alumni":
        a = 0
    elif session['session_type'] == "company":
        a = 1
    if request.method == 'POST':
        code1 = int(request.form.get('code'))
        code = session.get('verification_code1')
        if code != code1:
            flash("Verification code is wrong", category='error')
        else:
            new_user = session.get('new_user')
            new_user.login_first = 1
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            if a == 1:
                return redirect(url_for('auth.companylogin'))
            elif a == 0:
                return redirect(url_for('auth.alumnilogin'))
    return render_template("emailverification1.html", user=current_user, a=a)


@auth.route('/alumnisign-up', methods=['GET', 'POST'])
def alumnisign_up():
    session['session_type'] = "alumni"
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            code = random.randint(100000, 999999)
            session['verification_code1'] = code
            session['reset_email'] = email

            sender_email = "thegreatmanbhargav@gmail.com"
            sender_password = "hedjojqqxanjwvup"
            recipient_email = email
            subject = "Email verification"
            body = "The email verification code is:" + str(code)
            send_email(sender_email, sender_password, recipient_email, subject, body)

            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            session['new_user'] = new_user
            return redirect(url_for('auth.emailverification1'))

    return render_template("alumnisign_up.html", user=current_user)


@auth.route('/companysign-up', methods=['GET', 'POST'])
def companysign_up():
    session['session_type'] = "company"
    if request.method == 'POST':
        email = request.form.get('email')
        company_name = request.form.get('companyName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Company_User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(company_name) < 2:
            flash('company name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            code = random.randint(100000, 999999)
            session['verification_code1'] = code
            session['reset_email'] = email

            sender_email = "thegreatmanbhargav@gmail.com"
            sender_password = "hedjojqqxanjwvup"
            recipient_email = email
            subject = "Email verification"
            body = "The email verification code is:" + str(code)
            send_email(sender_email, sender_password, recipient_email, subject, body)

            new_user = Company_User(email=email, company_name=company_name, password=generate_password_hash(
                password1, method='sha256'))
            session['new_user'] = new_user
            return redirect(url_for('auth.emailverification1'))

    return render_template("companysign_up.html", user=current_user)
