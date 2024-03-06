from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    login_first = db.Column(db.Integer)  # New attribute
    age = db.Column(db.Integer)
    contactno = db.Column(db.String(20))
    year_of_graduation = db.Column(db.String(4))
    department = db.Column(db.String(100))
    USN = db.Column(db.String(15))
    resume_link = db.Column(db.String(200))
    notes = db.relationship('Note')


class Company_User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    company_name = db.Column(db.String(150))
    jobs = db.relationship('Job', backref='company__user', primaryjoin="Company_User.id == Job.company__user_id")

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, name="job_id")
    title = db.Column(db.String(150), name="job_title")
    qualifications_required = db.Column(db.String(500))
    additional_requirements = db.Column(db.String(500))
    company__user_id = db.Column(db.Integer, db.ForeignKey('company__user.id'))

class JobApplied(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

class JobAccepted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer, nullable=False)