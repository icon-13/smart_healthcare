import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_to_a_secure_key'
    # ✅ Use your PostgreSQL URL:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://icon:IPoyVOnTinzf9uMsiCxH4v55Z8fHXMC3@dpg-d1f7tnje5dus73fm2b5g-a.frankfurt-postgres.render.com/smart_healthcare_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
