from flask import Blueprint, render_template, redirect, request, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload

from app import db, login_manager
from app.models import Doctor, Patient, Note

# Keep track of last scanned UID (used by /scan page)
latest_uid = {"uid": None}

auth_bp = Blueprint('auth', __name__)

# --- Home Page ---
@auth_bp.route('/')
def home():
    return render_template('home.html')

# --- Load Doctor user for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))

# --- Doctor Sign Up ---
@auth_bp.route('/signup_doctor', methods=['GET', 'POST'])
def signup_doctor():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if Doctor.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('auth.signup_doctor'))

        new_doc = Doctor(username=username, password=generate_password_hash(password))
        db.session.add(new_doc)
        db.session.commit()
        flash("Doctor account created!", "success")
        return redirect(url_for('auth.login'))

    return render_template('signup_doctor.html')

# --- Doctor Login ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and check_password_hash(doctor.password, password):
            login_user(doctor)
            flash("Logged in successfully!", "success")
            return redirect(url_for('auth.doctor_dashboard'))

        flash("Invalid login credentials.", "danger")

    return render_template('login.html')

# --- Doctor Logout ---
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))

# --- Patient Sign Up ---
@auth_bp.route('/signup_patient', methods=['GET', 'POST'])
def signup_patient():
    if request.method == 'POST':
        uid = request.form.get('uid')
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        domicile = request.form.get('domicile')
        occupation = request.form.get('occupation')
        password = request.form.get('password')

        new_patient = Patient(
            rfid_uid=uid,
            name=name,
            age=age,
            gender=gender,
            domicile=domicile,
            occupation=occupation,
            password=generate_password_hash(password)
        )
        db.session.add(new_patient)
        db.session.commit()

        latest_uid["uid"] = None  # ✅ Clear the UID after registration

        flash("Patient registered successfully!", "success")
        return redirect(url_for('auth.view_patient_info', uid=uid))

    uid = request.args.get('uid')
    return render_template('signup_patient.html', uid=uid)


# --- Patient Login ---
@auth_bp.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        rfid_uid = request.form.get('rfid_uid')
        password = request.form.get('password')

        patient = Patient.query.filter_by(rfid_uid=rfid_uid).first()
        if patient and check_password_hash(patient.password, password):
            session['patient_id'] = patient.id
            flash("Logged in successfully!", "success")
            return redirect(url_for('auth.patient_profile'))

        flash("Invalid RFID UID or password.", "danger")

    return render_template('patient_login.html')

# --- Patient Profile ---
@auth_bp.route('/patient_profile')
def patient_profile():
    patient_id = session.get('patient_id')
    if not patient_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.patient_login'))

    patient = Patient.query.options(joinedload(Patient.notes)).get(patient_id)
    if not patient:
        flash("Patient not found.", "danger")
        session.pop('patient_id')
        return redirect(url_for('auth.patient_login'))

    return render_template('patient_profile.html', patient=patient)

# --- Patient Logout ---
@auth_bp.route('/logout_patient')
def logout_patient():
    session.pop('patient_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.patient_login'))

# --- Doctor Dashboard (List Patients) ---
@auth_bp.route('/dashboard')
@login_required
def doctor_dashboard():
    patients = Patient.query.all()
    return render_template('dashboard.html', patients=patients)

# --- Edit Patient (Doctor only) ---
@auth_bp.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.domicile = request.form.get('domicile')
        patient.occupation = request.form.get('occupation')

        notes_text = request.form.get('notes')
        if notes_text:
            new_note = Note(content=notes_text, patient=patient)
            db.session.add(new_note)

        db.session.commit()
        flash("Patient updated successfully.", "success")
        return redirect(url_for('auth.doctor_dashboard'))

    return render_template('edit_patient.html', patient=patient)

# --- Delete Patient (Doctor only) ---
@auth_bp.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted successfully.", "success")
    return redirect(url_for('auth.doctor_dashboard'))

# --- Scan RFID page ---
@auth_bp.route('/scan', methods=['GET', 'POST'])
def scan():
    global latest_uid
    if request.method == 'POST':
        uid = request.form.get('uid')
        if not uid:
            flash("No UID received.", "danger")
            return redirect(url_for('auth.scan'))

        patient = Patient.query.filter_by(rfid_uid=uid).first()
        if patient:
            latest_uid['uid'] = None  # Reset after use
            return redirect(url_for('auth.view_patient_info', uid=uid))
        else:
            flash(f"New card detected: {uid}. Please register patient.", "info")
            return redirect(url_for('auth.signup_patient', uid=uid))

    return render_template('scan.html')

# --- View Patient Info (public or doctor only) ---
@auth_bp.route('/patient_info/<uid>')
def view_patient_info(uid):
    patient = Patient.query.filter_by(rfid_uid=uid).first()
    if not patient:
        return "Patient not found", 404

    latest_uid["uid"] = None  # ✅ Clear the UID after viewing

    return render_template('patient_info.html', patient=patient)


# --- API Endpoint to receive UID from ESP8266 ---
@auth_bp.route('/api/receive_uid', methods=['POST'])
def receive_uid():
    data = request.get_json()
    uid = data.get('uid')

    if not uid:
        return jsonify({"error": "No UID provided"}), 400

    latest_uid['uid'] = uid
    return jsonify({"message": "UID received"}), 200

# --- API to get latest scanned UID for scan page JS ---
@auth_bp.route('/api/get_latest_uid')
def get_latest_uid():
    uid = latest_uid.get("uid")
    if uid:
        latest_uid["uid"] = None  # ✅ Clear it after one use
        return jsonify({"uid": uid})
    return jsonify({"uid": None})


# --- Test route ---
@auth_bp.route('/test')
def test():
    return "Test route works"
