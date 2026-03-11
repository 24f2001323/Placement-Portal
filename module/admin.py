from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from db import init_db, Admin, Company, Student, JobPosition, Application

app = Flask(__name__)
db_session = init_db()

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403
    total_companies = db_session.query(Company).count()
    total_students = db_session.query(Student).count()
    total_jobs = db_session.query(JobPosition).count()
    total_applications = db_session.query(Application).count()
    return render_template(
        "dashboard_admin.html",
        total_companies=total_companies,
        total_students=total_students,
        total_jobs=total_jobs,
        total_applications=total_applications
    )

@app.route("/admin/companies")
@login_required
def manage_companies():
    if current_user.role != "admin":
        return "Unauthorized", 403
    companies = db_session.query(Company).all()
    return render_template("manage_companies.html", companies=companies)

@app.route("/admin/approve_company/<int:company_id>")
@login_required
def approve_company(company_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    company = db_session.query(Company).filter_by(id=company_id).first()
    if company:
        company.approved = True
        db_session.commit()
        flash(f"Company '{company.name}' approved.")
    return redirect(url_for("manage_companies"))

@app.route("/admin/reject_company/<int:company_id>")
@login_required
def reject_company(company_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    company = db_session.query(Company).filter_by(id=company_id).first()
    if company:
        db_session.delete(company)
        db_session.commit()
        flash(f"Company '{company.name}' rejected and removed.")
    return redirect(url_for("manage_companies"))

@app.route("/admin/jobs")
@login_required
def manage_jobs():
    if current_user.role != "admin":
        return "Unauthorized", 403
    jobs = db_session.query(JobPosition).all()
    return render_template("manage_jobs.html", jobs=jobs)

@app.route("/admin/approve_job/<int:job_id>")
@login_required
def approve_job(job_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    job = db_session.query(JobPosition).filter_by(id=job_id).first()
    if job:
        job.approved = True
        db_session.commit()
        flash(f"Job '{job.title}' approved.")
    return redirect(url_for("manage_jobs"))

@app.route("/admin/reject_job/<int:job_id>")
@login_required
def reject_job(job_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    job = db_session.query(JobPosition).filter_by(id=job_id).first()
    if job:
        db_session.delete(job)
        db_session.commit()
        flash(f"Job '{job.title}' rejected and removed.")
    return redirect(url_for("manage_jobs"))

@app.route("/admin/students")
@login_required
def manage_students():
    if current_user.role != "admin":
        return "Unauthorized", 403
    students = db_session.query(Student).all()
    return render_template("manage_students.html", students=students)

@app.route("/admin/search_student", methods=["GET"])
@login_required
def search_student():
    if current_user.role != "admin":
        return "Unauthorized", 403
    query = request.args.get("q", "")
    students = db_session.query(Student).filter(
        (Student.name.contains(query)) |
        (Student.email.contains(query)) |
        (Student.id.contains(query))
    ).all()
    return render_template("manage_students.html", students=students)

@app.route("/admin/search_company", methods=["GET"])
@login_required
def search_company():
    if current_user.role != "admin":
        return "Unauthorized", 403
    query = request.args.get("q", "")
    companies = db_session.query(Company).filter(
        (Company.name.contains(query)) |
        (Company.website.contains(query))
    ).all()
    return render_template("manage_companies.html", companies=companies)

@app.route("/admin/deactivate_student/<int:student_id>")
@login_required
def deactivate_student(student_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    student = db_session.query(Student).filter_by(id=student_id).first()
    if student:
        db_session.delete(student)
        db_session.commit()
        flash(f"Student '{student.name}' deactivated.")
    return redirect(url_for("manage_students"))

@app.route("/admin/deactivate_company/<int:company_id>")
@login_required
def deactivate_company(company_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    company = db_session.query(Company).filter_by(id=company_id).first()
    if company:
        db_session.delete(company)
        db_session.commit()
        flash(f"Company '{company.name}' deactivated.")
    return redirect(url_for("manage_companies"))