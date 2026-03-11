from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, company, student
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

    @property
    def is_active(self):
        return self.is_active_user


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(100))
    hr_email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    address = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_blacklisted = db.Column(db.Boolean, default=False)

    drives = db.relationship('PlacementDrive', backref='company', cascade='all, delete-orphan')


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    tenth_percentage = db.Column(db.Float)
    twelfth_percentage = db.Column(db.Float)
    year_of_passing = db.Column(db.Integer)
    resume_path = db.Column(db.String(300))
    is_blacklisted = db.Column(db.Boolean, default=False)

    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan')


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    min_cgpa = db.Column(db.Float, default=0.0)
    package_lpa = db.Column(db.String(50))
    location = db.Column(db.String(150))
    job_type = db.Column(db.String(50), default='Full-time')  # Full-time, Internship
    deadline = db.Column(db.Date, nullable=False)
    max_applications = db.Column(db.Integer, default=0)  # 0 = unlimited
    status = db.Column(db.String(20), default='pending')  # pending, approved, closed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship('Application', backref='drive', cascade='all, delete-orphan')


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    applied_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='Applied')  # Applied, Shortlisted, Selected, Rejected
    remarks = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
    )
