from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Company, PlacementDrive, Application
from forms import CompanyProfileForm, PlacementDriveForm, ApplicationStatusForm

company_bp = Blueprint('company', __name__, url_prefix='/company')


def company_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    company = current_user.company
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    drive_stats = []
    for drive in drives:
        app_count = Application.query.filter_by(drive_id=drive.id).count()
        drive_stats.append({'drive': drive, 'app_count': app_count})
    total_apps = sum(d['app_count'] for d in drive_stats)
    return render_template('company/dashboard.html', company=company,
                           drive_stats=drive_stats, total_apps=total_apps)


@company_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@company_required
def profile():
    company = current_user.company
    form = CompanyProfileForm(obj=company)
    if form.validate_on_submit():
        company.name = form.company_name.data
        company.hr_contact = form.hr_contact.data
        company.hr_email = form.hr_email.data
        company.phone = form.phone.data
        company.website = form.website.data
        company.industry = form.industry.data
        company.description = form.description.data
        company.address = form.address.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('company.profile'))
    elif request.method == 'GET':
        form.company_name.data = company.name
    return render_template('company/profile.html', form=form, company=company)


@company_bp.route('/drives')
@login_required
@company_required
def my_drives():
    company = current_user.company
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    return render_template('company/my_drives.html', drives=drives, company=company)


@company_bp.route('/drives/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_drive():
    company = current_user.company
    if company.approval_status != 'approved':
        flash('Your company must be approved by admin before creating drives.', 'warning')
        return redirect(url_for('company.dashboard'))
    if company.is_blacklisted:
        flash('Your company has been blacklisted. Contact admin.', 'danger')
        return redirect(url_for('company.dashboard'))

    form = PlacementDriveForm()
    if form.validate_on_submit():
        drive = PlacementDrive(
            company_id=company.id,
            job_title=form.job_title.data,
            description=form.description.data,
            eligibility=form.eligibility.data,
            min_cgpa=form.min_cgpa.data or 0.0,
            package_lpa=form.package_lpa.data,
            location=form.location.data,
            job_type=form.job_type.data,
            deadline=form.deadline.data,
            max_applications=form.max_applications.data or 0,
            status='pending'
        )
        db.session.add(drive)
        db.session.commit()
        flash('Placement drive created. Awaiting admin approval.', 'success')
        return redirect(url_for('company.my_drives'))

    return render_template('company/create_drive.html', form=form)


@company_bp.route('/drives/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.company.id:
        abort(403)
    if drive.status == 'closed':
        flash('Cannot edit a closed drive.', 'warning')
        return redirect(url_for('company.my_drives'))

    form = PlacementDriveForm(obj=drive)
    if form.validate_on_submit():
        drive.job_title = form.job_title.data
        drive.description = form.description.data
        drive.eligibility = form.eligibility.data
        drive.min_cgpa = form.min_cgpa.data or 0.0
        drive.package_lpa = form.package_lpa.data
        drive.location = form.location.data
        drive.job_type = form.job_type.data
        drive.deadline = form.deadline.data
        drive.max_applications = form.max_applications.data or 0
        db.session.commit()
        flash('Drive updated successfully.', 'success')
        return redirect(url_for('company.my_drives'))

    return render_template('company/edit_drive.html', form=form, drive=drive)


@company_bp.route('/drives/<int:id>/close', methods=['POST'])
@login_required
@company_required
def close_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.company.id:
        abort(403)
    drive.status = 'closed'
    db.session.commit()
    flash('Drive has been closed.', 'info')
    return redirect(url_for('company.my_drives'))


@company_bp.route('/drives/<int:id>/delete', methods=['POST'])
@login_required
@company_required
def delete_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.company.id:
        abort(403)
    db.session.delete(drive)
    db.session.commit()
    flash('Drive has been deleted.', 'danger')
    return redirect(url_for('company.my_drives'))


@company_bp.route('/drives/<int:id>/applications')
@login_required
@company_required
def drive_applications(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != current_user.company.id:
        abort(403)
    apps = Application.query.filter_by(drive_id=drive.id).order_by(Application.applied_date.desc()).all()
    return render_template('company/drive_applications.html', drive=drive, applications=apps)


@company_bp.route('/applications/<int:id>/status', methods=['POST'])
@login_required
@company_required
def update_application_status(id):
    app = Application.query.get_or_404(id)
    if app.drive.company_id != current_user.company.id:
        abort(403)
    form = ApplicationStatusForm()
    if form.validate_on_submit():
        app.status = form.status.data
        app.remarks = form.remarks.data
        db.session.commit()
        flash(f'Application status updated to {app.status}.', 'success')
    return redirect(url_for('company.drive_applications', id=app.drive_id))
