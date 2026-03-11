import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from models import db, User

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'placement-portal-secret-key-2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # Create tables and seed admin
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@portal.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
