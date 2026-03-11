# Placement Portal Application (PlaceHub)

A full-stack web application for managing campus placement activities, built with **Flask**, **Jinja2**, **Bootstrap 5**, and **SQLite**.

## Features

### Roles
- **Admin** – Pre-existing superuser who manages companies, students, and placement drives
- **Company** – Registers, gets approved by admin, then creates placement drives and manages applications
- **Student** – Registers, applies for drives, tracks application status, and manages profile/resume

### Core Functionality
- Role-based authentication and access control (Flask-Login)
- Admin dashboard with stats, approve/reject companies & drives, search, blacklist
- Company dashboard with drive CRUD, application review, status updates
- Student dashboard with drive browsing, one-click apply, duplicate prevention, placement history
- Resume upload (PDF) during registration and from profile
- CGPA-based eligibility checks
- Complete application status tracking (Applied → Shortlisted → Interview → Selected / Rejected)

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend:** Jinja2, HTML5, CSS3, Bootstrap 5
- **Database:** SQLite

## Setup & Run

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`

### Default Admin
- **Username:** `admin`
- **Password:** `admin123`

## Project Structure
```
portal/
├── app.py              # Flask app factory & config
├── models.py           # SQLAlchemy models
├── forms.py            # WTForms
├── routes/
│   ├── auth.py         # Login, register, logout
│   ├── admin.py        # Admin dashboard & management
│   ├── company.py      # Company dashboard & drives
│   └── student.py      # Student dashboard & applications
├── templates/          # Jinja2 templates
├── static/             # CSS, uploads
└── requirements.txt
```
