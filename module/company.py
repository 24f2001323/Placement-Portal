from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from db_module import init_db, Company, JobPosition, Application, Student

app = Flask(__name__)
db_session = init_db()

@app.route("/company/dashboard")
@login_required
def company_dashboard():
    if current_user.role != "company":
        return "Unauthorized", 403
    company = db_session.query(Company).filter_by(id=current_user.id).first()
    if not company or not company.approved:
        return "Company not approved", 403
    jobs = db_session.query(JobPosition).filter_by(company_id=company.id).all()
    applications = db_session.query(Application).join(JobPosition).filter(JobPosition.company_id==company.id).all()
    return render_template("dashboard_company.html", jobs=jobs, applications=applications)

@app.route("/company/post_job", methods=["GET", "POST"])
@login_required
def post_job():
    if current_user.role != "company":
        return "Unauthorized", 403
    company = db_session.query(Company).filter_by(id=current_user.id).first()
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")
        required_skills = request.form.get("skills")
        experience = request.form.get("experience")
        salary_range = request.form.get("salary_range")
        job = JobPosition(
            title=title,
            description=description,
            location=location,
            company_id=company.id,
            required_skills=required_skills,
            experience=experience,
            salary_range=salary_range,
            approved=False,
            status="Active"
        )
        db_session.add(job)
        db_session.commit()
        flash("Job posted successfully. Await admin approval.")
        return redirect(url_for("company_dashboard"))
    return render_template("post_job.html")

@app.route("/company/update_job_status/<int:job_id>/<string:status>")
@login_required
def update_job_status(job_id, status):
    if current_user.role != "company":
        return "Unauthorized", 403
    job = db_session.query(JobPosition).filter_by(id=job_id, company_id=current_user.id).first()
    if job:
        job.status = status
        db_session.commit()
        flash(f"Job '{job.title}' status updated to {status}.")
    return redirect(url_for("company_dashboard"))

@app.route("/company/review_application/<int:app_id>/<string:decision>")
@login_required
def review_application(app_id, decision):
    if current_user.role != "company":
        return "Unauthorized", 403
    application = db_session.query(Application).join(JobPosition).filter(
        Application.id==app_id,
        JobPosition.company_id==current_user.id
    ).first()
    if application:
        application.status = decision
        db_session.commit()
        flash(f"Application status updated to {decision}.")
    return redirect(url_for("company_dashboard"))

@app.route("/company/view_shortlisted")
@login_required
def view_shortlisted():
    if current_user.role != "company":
        return "Unauthorized", 403
    applications = db_session.query(Application).join(JobPosition).filter(
        JobPosition.company_id==current_user.id,
        Application.status.in_(["Shortlisted", "Selected"])
    ).all()
    students = [app.student for app in applications]
    return render_template("shortlisted_students.html", students=students, applications=applications)