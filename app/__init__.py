from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Use blueprint name + function name

    # Blueprint imports
    from app.views.auth import auth_bp
    from app.views.doctor import doctor_bp
    from app.views.patient import patient_bp
    from app.views.rfid import api_bp

    # Register Blueprints (no prefix = routes start at root)
    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(api_bp)

    return app


# Doctor user loader for Flask-Login
from app.models import Doctor

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))
