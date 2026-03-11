import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Company, Student
from forms import LoginForm, CompanyRegistrationForm, StudentRegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('company.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active_user:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            # Check company-specific restrictions
            if user.role == 'company' and user.company:
                if user.company.is_blacklisted:
                    flash('Your company has been blacklisted. Contact admin.', 'danger')
                    return redirect(url_for('auth.login'))
                if user.company.approval_status != 'approved':
                    flash('Your company registration is still pending approval.', 'warning')
                    return redirect(url_for('auth.login'))

            # Check student blacklist
            if user.role == 'student' and user.student and user.student.is_blacklisted:
                flash('Your account has been blacklisted. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('auth.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        # Check uniqueness
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register_company.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register_company.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role='company'
        )
        db.session.add(user)
        db.session.flush()

        company = Company(
            user_id=user.id,
            name=form.company_name.data,
            hr_contact=form.hr_contact.data,
            hr_email=form.hr_email.data,
            phone=form.phone.data,
            website=form.website.data,
            industry=form.industry.data,
            description=form.description.data,
            address=form.address.data,
            approval_status='pending'
        )
        db.session.add(company)
        db.session.commit()

        flash('Registration successful! Please wait for admin approval before logging in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_company.html', form=form)


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = StudentRegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register_student.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register_student.html', form=form)
        if Student.query.filter_by(roll_number=form.roll_number.data).first():
            flash('Roll number already registered.', 'danger')
            return render_template('auth/register_student.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role='student'
        )
        db.session.add(user)
        db.session.flush()

        # Handle resume upload
        resume_filename = None
        if form.resume.data:
            filename = secure_filename(f"resume_{form.roll_number.data}.pdf")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.resume.data.save(filepath)
            resume_filename = filename

        student = Student(
            user_id=user.id,
            name=form.name.data,
            roll_number=form.roll_number.data,
            email=form.email.data,
            phone=form.phone.data,
            branch=form.branch.data,
            cgpa=form.cgpa.data,
            tenth_percentage=form.tenth_percentage.data,
            twelfth_percentage=form.twelfth_percentage.data,
            year_of_passing=form.year_of_passing.data,
            resume_path=resume_filename
        )
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_student.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
