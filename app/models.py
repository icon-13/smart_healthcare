from app import db
from datetime import datetime
from flask_login import UserMixin

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=True)

    def get_id(self):
        return f"doctor:{self.id}"  # Add this line


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid_uid = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    domicile = db.Column(db.String(100), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=True)  # 🔸 Add this line


    # Relationship with notes
    notes = db.relationship('Note', back_populates='patient', cascade='all, delete-orphan', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    patient = db.relationship('Patient', back_populates='notes')

from app import db
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=True)  # Optional admin photo

    def get_id(self):
         return f"admin:{self.id}"  # for Admin
