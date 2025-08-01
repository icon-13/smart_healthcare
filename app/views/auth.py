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
from app.models import Admin, Doctor

@login_manager.user_loader
def load_user(user_id):
    # user_id is stored as "<role>:<id>" string
    if ':' in user_id:
        role, real_id = user_id.split(':', 1)
        if role == 'admin':
            return Admin.query.get(int(real_id))
        elif role == 'doctor':
            return Doctor.query.get(int(real_id))
    return None


# --- Doctor Sign Up ---
import os
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from app import db
from app.models import Doctor

@auth_bp.route('/signup_doctor', methods=['GET', 'POST'])
@login_required
#@admin_required
def signup_doctor():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        photo_file = request.files.get('photo')

        if Doctor.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('auth.signup_doctor'))

        photo_filename = None
        if photo_file and photo_file.filename != '':
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(upload_folder, photo_filename)
            photo_file.save(photo_path)

        new_doc = Doctor(username=username,
                         password=generate_password_hash(password),
                         photo=photo_filename)
        db.session.add(new_doc)
        db.session.commit()
        flash("Doctor account created!", "success")
        return redirect(url_for('auth.login'))

    return render_template('signup_doctor.html')

# --- Doctor Login ---
from flask_login import login_user
from werkzeug.security import check_password_hash

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin, remember=True)
            flash("Logged in as admin!", "success")
            return redirect(url_for('auth.admin_dashboard'))

        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and check_password_hash(doctor.password, password):
            login_user(doctor, remember=True)
            flash("Logged in as doctor!", "success")
            return redirect(url_for('auth.doctor_dashboard'))

        flash("Invalid username or password", "danger")

    return render_template('login.html')


# --- Doctor Logout ---
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))

# --- Patient Sign Up ---
import os
from werkzeug.utils import secure_filename
from flask import current_app

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
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
             flash("Passwords do not match!", "danger")
             return redirect(url_for('auth.signup_patient', uid=uid))

        photo_file = request.files.get('photo')

        photo_filename = None
        if photo_file and photo_file.filename != '':
            filename = secure_filename(photo_file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            photo_path = os.path.join(upload_folder, filename)
            photo_file.save(photo_path)
            photo_filename = filename

        new_patient = Patient(
            rfid_uid=uid,
            name=name,
            age=age,
            gender=gender,
            domicile=domicile,
            occupation=occupation,
            password=generate_password_hash(password),
            photo=photo_filename
        )
        db.session.add(new_patient)
        db.session.commit()

        latest_uid["uid"] = None  # Clear the UID after registration

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
    if request.method == 'POST':
        uid = request.form.get('uid')
        if not uid:
            flash("No UID received.", "danger")
            return redirect(url_for('auth.scan'))

        patient = Patient.query.filter_by(rfid_uid=uid).first()

        # Clear the uid_consumed flag to allow next scan
        session.pop('uid_consumed', None)

        if patient:
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
import time

# Global variable to store the latest scanned UID and timestamp
latest_uid = {"uid": None, "timestamp": 0}
UID_VALID_DURATION = 10  # seconds

@auth_bp.route('/api/receive_uid', methods=['POST'])
def receive_uid():
    data = request.get_json()
    uid = data.get('uid')
    if not uid:
        return jsonify({"error": "No UID provided"}), 400

    latest_uid['uid'] = uid
    latest_uid['timestamp'] = time.time()
    return jsonify({"message": "UID received"}), 200


#get latedt uid
@auth_bp.route('/api/get_latest_uid')
def get_latest_uid():
    now = time.time()
    if latest_uid["uid"] and (now - latest_uid["timestamp"] < UID_VALID_DURATION):
        return jsonify({"uid": latest_uid["uid"]})
    else:
        latest_uid["uid"] = None
        latest_uid["timestamp"] = 0
        return jsonify({"uid": None})


# --- Test route ---
@auth_bp.route('/test')
def test():
    return "Test route works"

#reset patient password
@auth_bp.route('/reset_patient_password', methods=['GET', 'POST'])
def reset_patient_password():
    if request.method == 'POST':
        uid = request.form.get('rfid_uid')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.reset_patient_password'))

        patient = Patient.query.filter_by(rfid_uid=uid).first()
        if not patient:
            flash("Patient not found!", "danger")
            return redirect(url_for('auth.reset_patient_password'))

        patient.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password reset successfully!", "success")
        return redirect(url_for('auth.patient_login'))

    return render_template('reset_patient_password.html')

#admin required routes
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        # Check if user is admin by checking user id format
        if not hasattr(current_user, 'get_id'):
            abort(403)
        user_id = current_user.get_id()
        if not user_id.startswith('admin:'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

#admin dashboard
@auth_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    doctors = Doctor.query.all()
    return render_template('admin_dashboard.html', doctors=doctors)


@auth_bp.route('/admin/add_doctor', methods=['POST'])
@login_required
@admin_required
def add_doctor():
    username = request.form['username']
    password = request.form['password']
    photo = request.files['photo']

    if Doctor.query.filter_by(username=username).first():
        flash("Doctor already exists.", "danger")
        return redirect(url_for('auth.admin_dashboard'))

    filename = None
    if photo:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join('static/uploads', filename))

    hashed_password = generate_password_hash(password)
    new_doctor = Doctor(username=username, password=hashed_password, photo=filename)
    db.session.add(new_doctor)
    db.session.commit()

    flash("Doctor added successfully.", "success")
    return redirect(url_for('auth.admin_dashboard'))
 
# doctor rest password    
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    user_id = current_user.get_id()

    if not user_id or not user_id.startswith('doctor:'):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('auth.reset_password'))

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for('auth.reset_password'))

        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password updated successfully.", "success")
        return redirect(url_for('auth.doctor_dashboard'))

    return render_template('reset_password.html')


@auth_bp.route('/doctor/forgot_password', methods=['GET', 'POST'])
def forgot_doctor_password():
    if request.method == 'POST':
        username = request.form.get('username')
        doctor = Doctor.query.filter_by(username=username).first()
        if doctor:
            # Redirect to reset page (no token/email for now)
            return redirect(url_for('auth.reset_doctor_password', username=username))
        else:
            flash("Username not found.", "danger")

    return render_template('forgot_doctor_password.html')


@auth_bp.route('/doctor/reset_password/<username>', methods=['GET', 'POST'])
def reset_doctor_password(username):
    doctor = Doctor.query.filter_by(username=username).first()
    if not doctor:
        flash("Invalid reset link.", "danger")
        return redirect(url_for('auth.forgot_doctor_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
        else:
            doctor.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password reset successful. You can now log in.", "success")
            return redirect(url_for('auth.login'))

    return render_template('reset_doctor_password.html', username=username)


# Edit Doctor - GET shows form, POST processes update
@auth_bp.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        photo_file = request.files.get('photo')

        # Check if username is changing and if new username already exists
        if username != doctor.username and Doctor.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('auth.edit_doctor', doctor_id=doctor_id))

        doctor.username = username

        if photo_file and photo_file.filename != '':
            from werkzeug.utils import secure_filename
            import os
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(upload_folder, filename)
            photo_file.save(photo_path)
            doctor.photo = filename

        db.session.commit()
        flash("Doctor updated successfully.", "success")
        return redirect(url_for('auth.admin_dashboard'))

    return render_template('edit_doctor.html', doctor=doctor)


@auth_bp.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash("Doctor deleted successfully.", "success")
    return redirect(url_for('auth.admin_dashboard'))  # <-- Return a redirect or response here
