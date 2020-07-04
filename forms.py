from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, SelectField
from wtforms.validators import data_required, Length, EqualTo, ValidationError
from handover.models import User, Bed, Patient


class RegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[data_required(), Length(min=2, max=20)])
    password = PasswordField('Password:', validators=[data_required(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password:', validators=[data_required(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[data_required(), Length(min=2, max=20)])
    password = PasswordField('Password:', validators=[data_required()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdmitForm(FlaskForm):
    identifying_number = StringField('Patient Number:', validators=[data_required()])
    presenting_complaint = TextAreaField('Presenting Complaint:', validators=[data_required()])
    past_medical_history = TextAreaField('Past Medical History:')
    past_surgical_history = TextAreaField('Past Surgical History:')
    medications = TextAreaField('Medications:')
    social_history = TextAreaField('Social History:')
    allergies = TextAreaField('Allergies:')
    investigations = TextAreaField('Investigations:')
    plan = TextAreaField('Plan:')
    date_of_birth = DateField('Date of Birth:', validators=[data_required()], format='%d-%m-%Y')
    assign_bed = SelectField('Select bed:', choices=[], validators=[data_required()])
    submit = SubmitField('Submit')

    def validate_identifying_number(self, identifying_number):
        patient = Patient.query.filter_by(identifying_number=identifying_number.data).first()
        if patient:
            raise ValidationError('This patient number is already in the system.')


class EditForm(FlaskForm):
    past_medical_history = TextAreaField('Past Medical History:')
    past_surgical_history = TextAreaField('Past Surgical History:')
    medications = TextAreaField('Medications:')
    social_history = TextAreaField('Social History:')
    allergies = TextAreaField('Allergies:')
    investigations = TextAreaField('Investigations:')
    plan = TextAreaField('Plan:')
    assign_bed = SelectField('Select bed:', choices=[], validators=[data_required()])
    submit = SubmitField('Submit')
