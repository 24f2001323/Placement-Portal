import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Student, PlacementDrive, Application, Company
from forms import StudentProfileForm

student_bp = Blueprint('student', __name__, url_prefix='/student')


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = current_user.student
    approved_drives = PlacementDrive.query.filter_by(status='approved').order_by(PlacementDrive.deadline.asc()).all()
    my_applications = Application.query.filter_by(student_id=student.id).order_by(Application.applied_date.desc()).all()
    applied_drive_ids = [a.drive_id for a in my_applications]
    stats = {
        'total_applied': len(my_applications),
        'shortlisted': sum(1 for a in my_applications if a.status == 'Shortlisted'),
        'selected': sum(1 for a in my_applications if a.status == 'Selected'),
        'rejected': sum(1 for a in my_applications if a.status == 'Rejected'),
    }
    return render_template('student/dashboard.html', student=student,
                           approved_drives=approved_drives,
                           my_applications=my_applications,
                           applied_drive_ids=applied_drive_ids,
                           stats=stats)


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    student = current_user.student
    form = StudentProfileForm(obj=student)
    if form.validate_on_submit():
        student.name = form.name.data
        student.email = form.email.data
        student.phone = form.phone.data
        student.branch = form.branch.data
        student.cgpa = form.cgpa.data
        student.tenth_percentage = form.tenth_percentage.data
        student.twelfth_percentage = form.twelfth_percentage.data
        student.year_of_passing = form.year_of_passing.data

        if form.resume.data:
            filename = secure_filename(f"resume_{student.roll_number}.pdf")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.resume.data.save(filepath)
            student.resume_path = filename

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', form=form, student=student)


@student_bp.route('/drives')
@login_required
@student_required
def drives():
    student = current_user.student
    search = request.args.get('search', '')
    query = PlacementDrive.query.filter_by(status='approved')
    if search:
        query = query.join(PlacementDrive.company).filter(
            db.or_(
                PlacementDrive.job_title.ilike(f'%{search}%'),
                PlacementDrive.location.ilike(f'%{search}%'),
                PlacementDrive.description.ilike(f'%{search}%'),
                Company.name.ilike(f'%{search}%')
            )
        )
    drives_list = query.order_by(PlacementDrive.deadline.asc()).all()
    applied_drive_ids = [a.drive_id for a in Application.query.filter_by(student_id=student.id).all()]
    return render_template('student/drives.html', drives=drives_list,
                           applied_drive_ids=applied_drive_ids, student=student, search=search)


@student_bp.route('/drives/<int:id>/apply', methods=['POST'])
@login_required
@student_required
def apply_drive(id):
    student = current_user.student
    drive = PlacementDrive.query.get_or_404(id)

    if student.is_blacklisted:
        flash('Your account has been blacklisted. Contact admin.', 'danger')
        return redirect(url_for('student.drives'))

    if drive.status != 'approved':
        flash('This drive is not accepting applications.', 'warning')
        return redirect(url_for('student.drives'))

    # Check duplicate
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        flash('You have already applied for this drive.', 'warning')
        return redirect(url_for('student.drives'))

    # Check CGPA eligibility
    if drive.min_cgpa and student.cgpa and student.cgpa < drive.min_cgpa:
        flash(f'You do not meet the minimum CGPA requirement of {drive.min_cgpa}.', 'danger')
        return redirect(url_for('student.drives'))

    # Check max applications
    if drive.max_applications > 0:
        current_count = Application.query.filter_by(drive_id=drive.id).count()
        if current_count >= drive.max_applications:
            flash('This drive has reached its maximum number of applications.', 'warning')
            return redirect(url_for('student.drives'))

    application = Application(student_id=student.id, drive_id=drive.id, status='Applied')
    db.session.add(application)
    db.session.commit()
    flash(f'Successfully applied for "{drive.job_title}".', 'success')
    return redirect(url_for('student.applications'))


@student_bp.route('/applications')
@login_required
@student_required
def applications():
    student = current_user.student
    apps = Application.query.filter_by(student_id=student.id).order_by(Application.applied_date.desc()).all()
    return render_template('student/my_applications.html', applications=apps)


@student_bp.route('/history')
@login_required
@student_required
def history():
    student = current_user.student
    selected = Application.query.filter_by(student_id=student.id, status='Selected').all()
    all_apps = Application.query.filter_by(student_id=student.id).order_by(Application.applied_date.desc()).all()
    return render_template('student/placement_history.html', selected=selected, all_apps=all_apps)
