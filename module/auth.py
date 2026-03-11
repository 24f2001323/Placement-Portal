from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_bcrypt import Bcrypt
from db import init_db, Admin, Student, Company

app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)
db_session = init_db()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    try:
        role, uid = user_id.split(":")
        return User(uid, role)
    except:
        return None

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")
        if role == "admin":
            admin = db_session.query(Admin).filter_by(email=email).first()
            if admin and bcrypt.check_password_hash(admin.password, password):
                login_user(User(admin.id, "admin"))
                return redirect(url_for("dashboard_admin"))
            flash("Invalid Admin credentials")
        elif role == "company":
            company = db_session.query(Company).filter_by(email=email).first()
            if company and company.approved and bcrypt.check_password_hash(company.password, password):
                login_user(User(company.id, "company"))
                return redirect(url_for("dashboard_company"))
            flash("Company not approved or invalid credentials")
        elif role == "student":
            student = db_session.query(Student).filter_by(email=email).first()
            if student and bcrypt.check_password_hash(student.password, password):
                login_user(User(student.id, "student"))
                return redirect(url_for("dashboard_student"))
            flash("Invalid Student credentials")
        else:
            flash("Select a valid role")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        student = Student(name=name, email=email, resume_link="", password=hashed_pw)
        db_session.add(student)
        db_session.commit()
        flash("Student registered successfully. Login now.")
        return redirect(url_for("login"))
    return render_template("register_student.html")

@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        company = Company(name=name, email=email, website="", password=hashed_pw, approved=False)
        db_session.add(company)
        db_session.commit()
        flash("Company registered successfully. Await admin approval.")
        return redirect(url_for("login"))
    return render_template("register_company.html")

@app.route("/dashboard/admin")
@login_required
def dashboard_admin():
    if current_user.role != "admin":
        return "Unauthorized", 403
    companies = db_session.query(Company).all()
    return render_template("dashboard_admin.html", companies=companies)

@app.route("/dashboard/company")
@login_required
def dashboard_company():
    if current_user.role != "company":
        return "Unauthorized", 403
    return render_template("dashboard_company.html")

@app.route("/dashboard/student")
@login_required
def dashboard_student():
    if current_user.role != "student":
        return "Unauthorized", 403
    return render_template("dashboard_student.html")

@app.route("/approve_company/<int:company_id>")
@login_required
def approve_company(company_id):
    if current_user.role != "admin":
        return "Unauthorized", 403
    company = db_session.query(Company).filter_by(id=company_id).first()
    if company:
        company.approved = True
        db_session.commit()
        flash(f"Company '{company.name}' approved successfully!")
    return redirect(url_for("dashboard_admin"))

if __name__ == "__main__":
    app.run(debug=True)