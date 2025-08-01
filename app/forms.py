from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.validators import EqualTo  # add this at the top with others

class PatientRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    domicile = StringField('Place of Domicile', validators=[DataRequired()])
    occupation = StringField('Occupation', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')


class PatientRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    domicile = StringField('Place of Domicile', validators=[DataRequired()])
    occupation = StringField('Occupation', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class ScanForm(FlaskForm):
    uid = StringField('RFID UID', validators=[DataRequired()])
    submit = SubmitField('Scan')
