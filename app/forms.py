from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, SelectField, PasswordField,
    SubmitField, TextAreaField
)
from wtforms.validators import (
    DataRequired, Length, NumberRange, EqualTo, Optional
)

# ------------------------------
# Patient Registration Form
# ------------------------------
class PatientRegistrationForm(FlaskForm):
    rfid_uid = StringField('RFID UID', validators=[DataRequired(message="RFID UID is required")])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    domicile = StringField('Domicile', validators=[DataRequired()])
    occupation = StringField('Occupation', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    doctor_id = SelectField('Assign Doctor', coerce=int, validators=[Optional()])
    submit = SubmitField('Register')

# ------------------------------
# Scan RFID Card Form
# ------------------------------
class ScanForm(FlaskForm):
    uid = StringField('RFID UID', validators=[DataRequired()])
    submit = SubmitField('Scan')

# ------------------------------
# Doctor Signup Form
# ------------------------------
class DoctorSignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

# ------------------------------
# Doctor Login Form
# ------------------------------
class DoctorLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ------------------------------
# Patient Login Form
# ------------------------------
class PatientLoginForm(FlaskForm):
    rfid_uid = StringField('RFID UID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ------------------------------
# Password Reset Request Form
# ------------------------------
class RequestResetForm(FlaskForm):
    rfid_uid = StringField('RFID UID', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

# ------------------------------
# Password Reset Form
# ------------------------------
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Reset Password')

# ------------------------------
# Edit Patient Form
# ------------------------------

class EditPatientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField(
        'Gender',
        choices=[('Male', 'Male'), ('Female', 'Female')],
        validators=[DataRequired()]
    )
    domicile = StringField('Domicile', validators=[DataRequired()])
    occupation = StringField('Occupation', validators=[DataRequired()])
    doctor_id = SelectField('Assigned Doctor', coerce=int, choices=[], validators=[Optional()])  # <-- fix here
    notes = TextAreaField('Add Doctor Note', validators=[Optional()])
    submit = SubmitField('Update')


#delete patient form
class DeletePatientForm(FlaskForm):
    submit = SubmitField('Delete')

#assign doctor form
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class AssignDoctorForm(FlaskForm):
    doctor_id = SelectField('Assign Doctor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')

#claim patient form
from flask_wtf import FlaskForm
from wtforms import SubmitField

class ClaimPatientForm(FlaskForm):
    submit = SubmitField('Claim')


#referal form
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ReferralForm(FlaskForm):
    department = SelectField("Department", coerce=int, validators=[DataRequired()])
    reason = TextAreaField("Reason", validators=[DataRequired()])
    submit = SubmitField("Send Referral")


from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class NoteForm(FlaskForm):
    content = TextAreaField("Add Note", validators=[DataRequired()])
    submit = SubmitField("Add Note")

# ✅ Basic patient edit form
class PatientForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[("Male", "Male"), ("Female", "Female")])
    domicile = StringField("Domicile", validators=[DataRequired()])
    occupation = StringField("Occupation", validators=[DataRequired()])
    submit = SubmitField("Save")
