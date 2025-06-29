from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import Patient
from app import db
from app.forms import DeletePatientForm,   EditPatientForm
from app.models import Note


doctor_bp = Blueprint('doctor', __name__)

# -------------------------------
# Doctor Dashboard
# -------------------------------
@doctor_bp.route('/dashboard')
@login_required
def doctor_dashboard():
    if session.get('role') != 'doctor':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login_doctor'))

    patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    delete_form = DeletePatientForm()
    return render_template('dashboard_doctor.html', patients=patients, delete_form=delete_form)

# -------------------------------
# Edit Patient Info
# -------------------------------
@doctor_bp.route('/edit-patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    form = EditPatientForm(obj=patient)

    if form.validate_on_submit():
        patient.name = form.name.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        patient.domicile = form.domicile.data
        patient.occupation = form.occupation.data

        if form.notes.data.strip():
            new_note = Note(content=form.notes.data.strip(), patient=patient)
            db.session.add(new_note)

        db.session.commit()
        flash('Patient record updated.')
        return redirect(url_for('doctor.doctor_dashboard'))

    return render_template('edit_patient.html', form=form, patient=patient)

# -------------------------------
# Delete Patient
# -------------------------------
@doctor_bp.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    form = DeletePatientForm()
    if form.validate_on_submit():
        patient = Patient.query.get_or_404(patient_id)
        if patient.doctor_id != current_user.id:
            flash("Access denied", "danger")
            return redirect(url_for('doctor.doctor_dashboard'))
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted.', 'success')
    else:
        flash('Invalid form submission.', 'danger')
    return redirect(url_for('doctor.doctor_dashboard'))
