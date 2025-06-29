import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect



db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # ✅ Load all config values from config.py
    app.config.from_object('config.Config')
    
    # ✅ Optionally override SECRET_KEY from env
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or app.config['SECRET_KEY']

    # ✅ Optionally override DB URL from env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or app.config['SQLALCHEMY_DATABASE_URI']

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # ✅ Initialize CSRF

    login_manager.login_view = 'auth.login_doctor'

    from app.views.auth import auth_bp
    from app.views.doctor import doctor_bp
    from app.views.patient import patient_bp
    from app.views.rfid import api_bp
    from app.views.lab import lab_bp
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(lab_bp)

    return app

from app.models import Doctor

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))
