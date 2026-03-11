from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, Company, Student, PlacementDrive, Application

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_drives': PlacementDrive.query.count(),
        'total_applications': Application.query.count(),
        'pending_companies': Company.query.filter_by(approval_status='pending').count(),
        'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
        'approved_companies': Company.query.filter_by(approval_status='approved').count(),
        'approved_drives': PlacementDrive.query.filter_by(status='approved').count(),
        'selected_students': Application.query.filter_by(status='Selected').count(),
    }
    recent_apps = Application.query.order_by(Application.applied_date.desc()).limit(5).all()
    pending_companies = Company.query.filter_by(approval_status='pending').limit(5).all()
    pending_drives = PlacementDrive.query.filter_by(status='pending').limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_apps=recent_apps,
                           pending_companies=pending_companies,
                           pending_drives=pending_drives)


# ─── Company Management ──────────────────────────────────────

@admin_bp.route('/companies')
@login_required
@admin_required
def companies():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    query = Company.query
    if search:
        query = query.filter(Company.name.ilike(f'%{search}%'))
    if status_filter != 'all':
        query = query.filter_by(approval_status=status_filter)
    companies_list = query.order_by(Company.id.desc()).all()
    return render_template('admin/companies.html', companies=companies_list,
                           search=search, status_filter=status_filter)


@admin_bp.route('/companies/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = 'approved'
    db.session.commit()
    flash(f'{company.name} has been approved.', 'success')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/companies/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'{company.name} has been rejected.', 'warning')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/companies/<int:id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_company(id):
    company = Company.query.get_or_404(id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    action = 'blacklisted' if company.is_blacklisted else 'unblacklisted'
    flash(f'{company.name} has been {action}.', 'info')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(id):
    company = Company.query.get_or_404(id)
    user = company.user
    db.session.delete(user)
    db.session.commit()
    flash(f'{company.name} has been deleted.', 'danger')
    return redirect(url_for('admin.companies'))


# ─── Student Management ──────────────────────────────────────

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    search = request.args.get('search', '')
    query = Student.query
    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f'%{search}%'),
                Student.roll_number.ilike(f'%{search}%'),
                Student.phone.ilike(f'%{search}%'),
                Student.email.ilike(f'%{search}%')
            )
        )
    students_list = query.order_by(Student.id.desc()).all()
    return render_template('admin/students.html', students=students_list, search=search)


@admin_bp.route('/students/<int:id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_student(id):
    student = Student.query.get_or_404(id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    action = 'blacklisted' if student.is_blacklisted else 'unblacklisted'
    flash(f'{student.name} has been {action}.', 'info')
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    user = student.user
    db.session.delete(user)
    db.session.commit()
    flash(f'{student.name} has been deleted.', 'danger')
    return redirect(url_for('admin.students'))


# ─── Drive Management ────────────────────────────────────────

@admin_bp.route('/drives')
@login_required
@admin_required
def drives():
    status_filter = request.args.get('status', 'all')
    query = PlacementDrive.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    drives_list = query.order_by(PlacementDrive.created_at.desc()).all()
    return render_template('admin/drives.html', drives=drives_list, status_filter=status_filter)


@admin_bp.route('/drives/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'approved'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been approved.', 'success')
    return redirect(url_for('admin.drives'))


@admin_bp.route('/drives/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'rejected'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been rejected.', 'warning')
    return redirect(url_for('admin.drives'))


# ─── Applications ────────────────────────────────────────────

@admin_bp.route('/applications')
@login_required
@admin_required
def applications():
    status_filter = request.args.get('status', 'all')
    query = Application.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    apps_list = query.order_by(Application.applied_date.desc()).all()
    return render_template('admin/applications.html', applications=apps_list, status_filter=status_filter)
