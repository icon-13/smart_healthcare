from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Patient
from app import db

patient_bp = Blueprint('patient', __name__)

# ----- Patient Sign Up (via scanned UID) -----
@patient_bp.route('/register-patient', methods=['GET', 'POST'])
def register_patient():
    uid = request.args.get('uid')

    if not uid:
        flash('No RFID UID provided.')
        return redirect(url_for('auth.login'))

    existing = Patient.query.filter_by(rfid_uid=uid).first()
    if existing:
        flash('Card already registered.')
        return redirect(url_for('patient.view_patient', uid=uid))

    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        contact = request.form['contact']

        new_patient = Patient(
            name=name,
            age=age,
            gender=gender,
            contact=contact,
            rfid_uid=uid
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('Patient registered successfully.')
        return redirect(url_for('patient.view_patient', uid=uid))

    return render_template('signup_patient.html', uid=uid)


# ----- View Patient Info (via UID) -----
@patient_bp.route('/patient-info')
def view_patient():
    uid = request.args.get('uid')
    patient = Patient.query.filter_by(rfid_uid=uid).first()

    if not patient:
        flash('No patient found for this UID.')
        return redirect(url_for('auth.login'))

    return render_template('patient_profile.html', patient=patient)
