from app import db
from models import Admin  # adjust import based on your project structure
from werkzeug.security import generate_password_hash

admin = Admin(username='admin', password=generate_password_hash('admin123'))
db.session.add(admin)
db.session.commit()
