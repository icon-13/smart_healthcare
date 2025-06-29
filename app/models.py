from app import db
from flask import current_app
from datetime import datetime
from flask_login import UserMixin


class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    visits = db.relationship('Visit', backref='doctor', lazy=True)
    sent_referrals = db.relationship('Referral', foreign_keys='Referral.from_doctor_id', backref='from_doctor')
    received_referrals = db.relationship('Referral', foreign_keys='Referral.to_doctor_id', backref='to_doctor')



from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid_uid = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    domicile = db.Column(db.String(100), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    visits = db.relationship('Visit', backref='patient', lazy=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)  # allow None
    doctor = db.relationship('Doctor', backref='patients')

    # Relationship with notes
    notes = db.relationship('Note', back_populates='patient', cascade='all, delete-orphan', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'patient_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            patient_id = data.get('patient_id')
        except Exception:
            return None
        return Patient.query.get(patient_id)

#notes model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    patient = db.relationship('Patient', back_populates='notes')

# receptionist model

class Receptionist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

#visit model
from datetime import datetime

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    prescriptions = db.relationship('Prescription', backref='visit', lazy=True)
    referrals = db.relationship('Referral', backref='visit', lazy=True)
    test_results = db.relationship('TestResult', backref='visit', lazy=True)

#department model
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    referrals = db.relationship('Referral', backref='department', lazy=True)

#refferal model
class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    from_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    to_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')

    from_doctor = db.relationship('Doctor', foreign_keys=[from_doctor_id], backref='sent_referrals')
    to_doctor = db.relationship('Doctor', foreign_keys=[to_doctor_id], backref='received_referrals')
    patient = db.relationship('Patient', backref='referrals')


#prescription model
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.id'))
    medication_name = db.Column(db.String(200))
    dosage = db.Column(db.String(100))
    instructions = db.Column(db.Text)
    dispensed = db.Column(db.Boolean, default=False)  # Pharmacy marks as dispensed

#lab test model
class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<LabTest {self.name}>"


#test result
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    lab_test_id = db.Column(db.Integer, db.ForeignKey('lab_test.id'), nullable=False)
    result = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, completed, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='test_results')
    doctor = db.relationship('Doctor', backref='ordered_tests')
    lab_test = db.relationship('LabTest')
