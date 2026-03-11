from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from db import init_db, Student, JobPosition, Application, Company
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
db_session = init_db()

UPLOAD_FOLDER = "uploads/resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return "Unauthorized", 403
    student = db_session.query(Student).filter_by(id=current_user.id).first()
    applications = db_session.query(Application).filter_by(student_id=student.id).all()
    return render_template("dashboard_student.html", student=student, applications=applications)

@app.route("/student/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    if current_user.role != "student":
        return "Unauthorized", 403
    student = db_session.query(Student).filter_by(id=current_user.id).first()
    if request.method == "POST":
        student.education = request.form.get("education")
        student.skills = request.form.get("skills")
        if "resume" in request.files:
            file = request.files["resume"]
            if file.filename != "":
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                student.resume_link = filepath
        db_session.commit()
        flash("Profile updated successfully.")
        return redirect(url_for("student_dashboard"))
    return render_template("update_profile.html", student=student)

@app.route("/student/jobs")
@login_required
def view_jobs():
    if current_user.role != "student":
        return "Unauthorized", 403
    query = request.args.get("q", "")
    jobs = db_session.query(JobPosition).filter(
        JobPosition.approved==True,
        JobPosition.status=="Active",
        (JobPosition.title.contains(query)) |
        (JobPosition.description.contains(query)) |
        (JobPosition.required_skills.contains(query))
    ).all()
    return render_template("view_jobs.html", jobs=jobs)

@app.route("/student/apply/<int:job_id>")
@login_required
def apply_job(job_id):
    if current_user.role != "student":
        return "Unauthorized", 403
    existing = db_session.query(Application).filter_by(student_id=current_user.id, job_id=job_id).first()
    if existing:
        flash("Already applied for this job.")
        return redirect(url_for("view_jobs"))
    application = Application(student_id=current_user.id, job_id=job_id, status="Pending")
    db_session.add(application)
    db_session.commit()
    flash("Applied successfully.")
    return redirect(url_for("student_dashboard"))

@app.route("/student/applied_jobs")
@login_required
def applied_jobs():
    if current_user.role != "student":
        return "Unauthorized", 403
    applications = db_session.query(Application).filter_by(student_id=current_user.id).all()
    return render_template("applied_jobs.html", applications=applications)