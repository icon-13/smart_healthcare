from flask import (
    Blueprint, render_template, redirect, request, url_for, flash,
    session, jsonify, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from functools import wraps

from app import db, login_manager
from app.models import (
    Doctor, Patient, Note, Receptionist, Visit,
    Department, Referral, LabTest, TestResult
)
from app.forms import (
    DoctorSignupForm, DoctorLoginForm, PatientRegistrationForm,
    PatientLoginForm, EditPatientForm, RequestResetForm, ResetPasswordForm,
    DeletePatientForm, AssignDoctorForm, ClaimPatientForm, NoteForm, ReferralForm
)

auth_bp = Blueprint('auth', __name__)
latest_uid = {"uid": None}

# ---------------------- HELPERS ----------------------

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))

def login_required_or_receptionist(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated or session.get('role') == 'receptionist':
            return f(*args, **kwargs)
        flash("Unauthorized", "danger")
        return redirect(url_for("auth.home"))
    return decorated

def receptionist_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') == 'receptionist':
            return f(*args, **kwargs)
        flash("Receptionist only!", "warning")
        return redirect(url_for("auth.login_receptionist"))
    return decorated

# ---------------------- GENERAL ----------------------

@auth_bp.route('/')
def home():
    return render_template('home.html')

# ---------------------- DOCTOR AUTH ----------------------

@auth_bp.route('/signup_doctor', methods=['GET', 'POST'])
def signup_doctor():
    form = DoctorSignupForm()
    if form.validate_on_submit():
        if Doctor.query.filter_by(username=form.username.data).first():
            flash("Username exists!", "danger")
            return redirect(url_for('auth.signup_doctor'))
        new_doc = Doctor(
            username=form.username.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_doc)
        db.session.commit()
        flash("Doctor account created!", "success")
        return redirect(url_for('auth.login_doctor'))
    return render_template('signup_doctor.html', form=form)

@auth_bp.route('/login/doctor', methods=['GET', 'POST'])
def login_doctor():
    form = DoctorLoginForm()
    if form.validate_on_submit():
        doctor = Doctor.query.filter_by(username=form.username.data).first()
        if doctor and check_password_hash(doctor.password, form.password.data):
            login_user(doctor)
            session['role'] = 'doctor'
            flash("Logged in!", "success")
            return redirect(url_for('auth.doctor_dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login_doctor.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('role', None)
    flash("Logged out.", "info")
    return redirect(url_for('auth.home'))

# ---------------------- DOCTOR DASHBOARD ----------------------

@auth_bp.route('/dashboard_doctor')
@login_required
def doctor_dashboard():
    if session.get("role") != "doctor":
        flash("Unauthorized.", "danger")
        return redirect(url_for("auth.home"))
    patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    delete_form = DeletePatientForm()
    return render_template("dashboard_doctor.html", patients=patients, delete_form=delete_form)

# ---------------------- RECEPTIONIST ----------------------

@auth_bp.route('/signup_receptionist', methods=['GET', 'POST'])
def signup_receptionist():
    form = DoctorSignupForm()
    if form.validate_on_submit():
        if Receptionist.query.filter_by(username=form.username.data).first():
            flash("Username exists!", "danger")
            return redirect(url_for('auth.signup_receptionist'))
        new_rec = Receptionist(
            username=form.username.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_rec)
        db.session.commit()
        flash("Receptionist created!", "success")
        return redirect(url_for('auth.login_receptionist'))
    return render_template('signup_receptionist.html', form=form)

@auth_bp.route('/login_receptionist', methods=['GET', 'POST'])
def login_receptionist():
    form = DoctorLoginForm()
    if form.validate_on_submit():
        receptionist = Receptionist.query.filter_by(username=form.username.data).first()
        if receptionist and check_password_hash(receptionist.password, form.password.data):
            session['role'] = 'receptionist'
            flash("Logged in!", "success")
            return redirect(url_for('auth.signup_patient'))
        flash("Invalid credentials.", "danger")
    return render_template('login_receptionist.html', form=form)

@auth_bp.route('/logout_receptionist')
def logout_receptionist():
    session.pop('role', None)
    flash("Receptionist logged out.", "info")
    return redirect(url_for('auth.home'))

# ---------------------- PATIENT REGISTER ----------------------

@auth_bp.route('/signup_patient', methods=['GET', 'POST'])
@receptionist_required
def signup_patient():
    form = PatientRegistrationForm()
    form.doctor_id.choices = [(0, 'Unassigned')] + [
        (doc.id, doc.username) for doc in Doctor.query.order_by(Doctor.username).all()
    ]
    if form.validate_on_submit():
        if Patient.query.filter_by(rfid_uid=form.rfid_uid.data).first():
            flash("UID exists.", "danger")
            return redirect(url_for('auth.signup_patient'))
        new_patient = Patient(
            rfid_uid=form.rfid_uid.data.strip(),
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            domicile=form.domicile.data,
            occupation=form.occupation.data,
            password=generate_password_hash(form.password.data),
            doctor_id=form.doctor_id.data if form.doctor_id.data != 0 else None
        )
        db.session.add(new_patient)
        db.session.commit()
        latest_uid['uid'] = None
        flash("Patient registered!", "success")
        return redirect(url_for('auth.view_patient_info', uid=form.rfid_uid.data))
    return render_template('signup_patient.html', form=form)

# ---------------------- EDIT / DELETE PATIENT ----------------------

@auth_bp.route('/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required_or_receptionist
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    role = session.get("role")

    if role == "doctor" and patient.doctor_id != current_user.id:
        abort(403)

    form = EditPatientForm(obj=patient)
    form.doctor_id.choices = [(0, 'Unassigned')] + [
        (doc.id, doc.username) for doc in Doctor.query.order_by(Doctor.username).all()
    ]

    if form.validate_on_submit():
        patient.name = form.name.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        patient.domicile = form.domicile.data
        patient.occupation = form.occupation.data
        patient.doctor_id = form.doctor_id.data if form.doctor_id.data != 0 else None
        if form.notes.data.strip():
            db.session.add(Note(content=form.notes.data.strip(), patient=patient))
        db.session.commit()
        flash("Patient updated.", "success")
        return redirect(url_for('auth.doctor_dashboard'))

    return render_template('edit_patient.html', form=form, patient=patient)

# ---------------------- UNASSIGNED & ASSIGNED ----------------------

@auth_bp.route('/unassigned-patients', methods=['GET', 'POST'])
@login_required_or_receptionist
def unassigned_patients():
    patients = Patient.query.filter_by(doctor_id=None).all()
    assign_form = AssignDoctorForm()
    claim_form = ClaimPatientForm()
    assign_form.doctor_id.choices = [(d.id, f"Dr. {d.username}") for d in Doctor.query.all()]

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        if "assign" in request.form and session.get("role") == "receptionist":
            patient = Patient.query.get_or_404(patient_id)
            patient.doctor_id = assign_form.doctor_id.data
            db.session.commit()
            flash("Assigned!", "success")
        elif "claim" in request.form and session.get("role") == "doctor":
            patient = Patient.query.get_or_404(patient_id)
            patient.doctor_id = current_user.id
            db.session.commit()
            flash("Claimed!", "success")
        return redirect(url_for("auth.unassigned_patients"))

    return render_template(
        "unassigned_patients.html",
        patients=patients,
        assign_form=assign_form,
        claim_form=claim_form
    )

@auth_bp.route('/assigned-patients')
@login_required_or_receptionist
def assigned_patients():
    patients = Patient.query.filter(Patient.doctor_id != None).all()
    return render_template('assigned_patients.html', patients=patients)

# ---------------------- PATIENT VIEWS ----------------------

@auth_bp.route('/scan')
def scan():
    uid = request.args.get('uid')
    if uid:
        patient = Patient.query.filter_by(rfid_uid=uid).first()
        if patient:
            return redirect(url_for('auth.view_patient_info', uid=uid))
        return redirect(url_for('auth.signup_patient', uid=uid))
    return render_template('scan.html')

@auth_bp.route('/patient_info/<uid>')
def view_patient_info(uid):
    patient = Patient.query.filter_by(rfid_uid=uid).first_or_404()
    return render_template('patient_info.html', patient=patient)

# ---------------------- PATIENT LOGIN ----------------------

@auth_bp.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    form = PatientLoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(rfid_uid=form.rfid_uid.data).first()
        if patient and check_password_hash(patient.password, form.password.data):
            session['patient_id'] = patient.id
            flash("Logged in!", "success")
            return redirect(url_for('auth.patient_profile'))
    return render_template('patient_login.html', form=form)

@auth_bp.route('/patient_profile')
def patient_profile():
    pid = session.get('patient_id')
    patient = Patient.query.get_or_404(pid)
    return render_template('patient_profile.html', patient=patient)

@auth_bp.route('/logout_patient')
def logout_patient():
    session.pop('patient_id', None)
    flash("Logged out.", "info")
    return redirect(url_for('auth.patient_login'))

# ---------------------- DOCTOR PATIENT DETAIL & NOTES ----------------------

@auth_bp.route("/patient/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.doctor_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("auth.doctor_dashboard"))
    return render_template("patient_detail.html", patient=patient, note_form=NoteForm())

@auth_bp.route("/patient/<int:patient_id>/add-note", methods=["POST"])
@login_required
def add_note(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = NoteForm()
    if form.validate_on_submit():
        db.session.add(Note(content=form.content.data, patient_id=patient.id))
        db.session.commit()
        flash("Note added!", "success")
    return redirect(url_for('auth.patient_detail', patient_id=patient.id))


#depatment dashboard 

from flask import request

@auth_bp.route('/department/<int:dept_id>/dashboard')
@login_required
def department_dashboard(dept_id):
    dept = Department.query.get_or_404(dept_id)
    # Show all pending referrals assigned to this department
    referrals = Referral.query.filter_by(department_id=dept.id, status='pending').all()
    return render_template('department_dashboard.html', department=dept, referrals=referrals)

#process refferal
@auth_bp.route('/referral/<int:referral_id>/process', methods=['GET', 'POST'])
@login_required
def process_referral(referral_id):
    referral = Referral.query.get_or_404(referral_id)
    if request.method == 'POST':
        # Mark referral as completed or update notes if needed
        referral.status = 'completed'
        db.session.commit()
        flash('Referral marked as completed.', 'success')
        return redirect(url_for('auth.department_dashboard', dept_id=referral.department_id))
    return render_template('process_referral.html', referral=referral)
