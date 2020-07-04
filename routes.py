from flask import render_template, redirect, flash, url_for, request
from handover import app, db, bcrypt
from handover.forms import RegistrationForm, LoginForm, AdmitForm, EditForm
from handover.models import User, Bed, Patient
from flask_login import login_user, logout_user, current_user, login_required
from handover.helpers import bed_choices, flash_errors




@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # redirect to homepage if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # redirect to homepage if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # find if the user exists by looking up his name
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if user was redirected to login page send him back to origin
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessfull. Check Username / Password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    "Will allow a new user to logout"
    logout_user()
    return redirect(url_for('home'))


@app.route('/patient_list', methods=['GET', 'POST'])
@login_required
def patient_list():
    "Will display all patients currently admitted on the ward"
    # TODO add a way to select which wards to see
    beds = Bed.query.all()
    return render_template('patient_list.html', title='Patient List', beds=beds)


@app.route('/admit', methods = ['GET', 'POST'])
@login_required
def admit():
    "Will allow user to add a patient to the list"
    form = AdmitForm()
    # populate a list of all the empty beds for the drop down list
    form.assign_bed.choices = bed_choices()
    if form.validate_on_submit():
        patient = Patient(identifying_number = form.identifying_number.data, 
                            presenting_complaint = form.presenting_complaint.data,
                            past_medical_history = form.past_medical_history.data,
                            past_surgical_history = form.past_surgical_history.data,
                            medications = form.medications.data,
                            social_history = form.social_history.data,
                            allergies = form.allergies.data,
                            investigations = form.investigations.data,
                            plan = form.plan.data,
                            date_of_birth = form.date_of_birth.data,) 
        bed=Bed.query.filter_by(bed_number = form.assign_bed.data).first()
        bed.patient_id = form.identifying_number.data
        bed.user_id = current_user.id
        db.session.add(patient)
        db.session.commit()
        flash(f'Patient ID {form.identifying_number.data} added to bed {form.assign_bed.data}.', 'success')
        return redirect(url_for('patient_list'))
    return render_template('admit.html', title='Admit Patient', form=form)


@app.route('/patient/<pn>', methods=['GET', 'POST'])
@login_required
def patient(pn):
    "Will display infromation about the selected patient"
    patient = Patient.query.filter_by(identifying_number=pn).first()
    bed = Bed.query.filter_by(patient_id = patient.identifying_number).first()
    return render_template('patient.html', title='Patient info', patient=patient, bed=bed)


@app.route('/patient/<pn>/edit', methods=['GET', 'POST'])
@login_required
def edit(pn):
    "Will allow user to view and edit information about selected patient"
    patient = Patient.query.filter_by(identifying_number=pn).first()
    form = EditForm()
    form.assign_bed.choices = bed_choices(pn)
    if request.method == 'POST' and form.validate_on_submit:
        patient.past_medical_history = form.past_medical_history.data
        patient.past_surgical_history = form.past_surgical_history.data
        patient.medications = form.medications.data
        patient.social_history = form.social_history.data
        patient.allergies = form.allergies.data
        patient.investigations = form.investigations.data
        patient.plan = form.plan.data
        current_bed = Bed.query.filter_by(patient_id = pn).first()
        current_bed.patient_id = None  # Set the old bed back to empty
        new_bed=Bed.query.filter_by(bed_number = form.assign_bed.data).first()
        new_bed.patient_id = pn # assign patient to new bed
        new_bed.user_id, current_bed.user_id = current_user.id, current_user.id
        db.session.commit()
        flash('Patient information updated successfuly', 'success')
        return redirect(url_for('patient_list'))
    form.past_medical_history.data = patient.past_medical_history
    form.past_surgical_history.data = patient.past_surgical_history
    form.medications.data = patient.medications
    form.social_history.data = patient.social_history
    form.allergies.data = patient.allergies
    form.investigations.data = patient.investigations
    form.plan.data = patient.plan
    return render_template('edit.html', title='Edit patient info', form=form, patient=patient)


@app.route('/patient/<pn>/discharge', methods=['POST'])
@login_required
def discharge(pn):
    "Will allow user to remove a patient from the database"
    patient = Patient.query.filter_by(identifying_number = pn).first()
    bed = Bed.query.filter_by(patient_id = pn).first()
    bed.patient_id = None
    db.session.delete(patient)
    db.session.commit()
    flash('Patient has been discharged', 'danger')
    return redirect(url_for('patient_list'))


########################################  TODO  ###########################################################

# Add functionality