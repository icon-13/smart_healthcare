from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Patient
from app import db

doctor_bp = Blueprint('doctor', __name__)

# ----- Doctor Dashboard -----
@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    patients = Patient.query.all()
    return render_template('dashboard_doctor.html', patients=patients)

# ----- Edit Patient Info -----
@doctor_bp.route('/edit-patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.diagnosis = request.form['diagnosis']
        patient.treatment = request.form['treatment']
        db.session.commit()
        flash('Patient record updated.')
        return redirect(url_for('doctor.dashboard'))

    return render_template('edit_patient.html', patient=patient)
