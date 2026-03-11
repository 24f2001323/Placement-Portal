from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, TextAreaField, FloatField,
                     IntegerField, SelectField, DateField, SubmitField)
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo


# ─── Auth Forms ───────────────────────────────────────────────

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CompanyRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=150)])
    hr_contact = StringField('HR Contact Person', validators=[DataRequired(), Length(max=100)])
    hr_email = StringField('HR Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    industry = StringField('Industry', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Company Description', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    submit = SubmitField('Register')


class StudentRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(max=30)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    branch = StringField('Branch / Department', validators=[Optional(), Length(max=100)])
    cgpa = FloatField('CGPA', validators=[Optional(), NumberRange(min=0, max=10)])
    tenth_percentage = FloatField('10th Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    twelfth_percentage = FloatField('12th Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    year_of_passing = IntegerField('Year of Passing', validators=[Optional()])
    resume = FileField('Upload Resume (PDF)', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    submit = SubmitField('Register')


# ─── Profile Forms ────────────────────────────────────────────

class CompanyProfileForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=150)])
    hr_contact = StringField('HR Contact Person', validators=[DataRequired(), Length(max=100)])
    hr_email = StringField('HR Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    industry = StringField('Industry', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Company Description', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    submit = SubmitField('Update Profile')


class StudentProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    branch = StringField('Branch / Department', validators=[Optional(), Length(max=100)])
    cgpa = FloatField('CGPA', validators=[Optional(), NumberRange(min=0, max=10)])
    tenth_percentage = FloatField('10th Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    twelfth_percentage = FloatField('12th Percentage', validators=[Optional(), NumberRange(min=0, max=100)])
    year_of_passing = IntegerField('Year of Passing', validators=[Optional()])
    resume = FileField('Upload Resume (PDF)', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    submit = SubmitField('Update Profile')


# ─── Drive Forms ──────────────────────────────────────────────

class PlacementDriveForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    eligibility = TextAreaField('Eligibility Criteria', validators=[Optional()])
    min_cgpa = FloatField('Minimum CGPA', validators=[Optional(), NumberRange(min=0, max=10)])
    package_lpa = StringField('Package (LPA)', validators=[Optional(), Length(max=50)])
    location = StringField('Location', validators=[Optional(), Length(max=150)])
    job_type = SelectField('Job Type', choices=[('Full-time', 'Full-time'), ('Internship', 'Internship'), ('Part-time', 'Part-time')])
    deadline = DateField('Application Deadline', validators=[DataRequired()])
    max_applications = IntegerField('Max Applications (0 = unlimited)', validators=[Optional()], default=0)
    submit = SubmitField('Create Drive')


class ApplicationStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Selected', 'Selected'),
        ('Placed', 'Placed'),
        ('Rejected', 'Rejected')
    ], validators=[DataRequired()])
    remarks = TextAreaField('Remarks', validators=[Optional()])
    submit = SubmitField('Update Status')
