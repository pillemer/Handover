from flask import render_template, redirect, flash, url_for, request
from handover import app, db, bcrypt
from handover.forms import RegistrationForm, LoginForm, AdmitForm, EditForm
from handover.models import User, Bed, Patient, Investigation
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
                            plan = form.plan.data,
                            date_of_birth = form.date_of_birth.data,) 
        bed=Bed.query.filter_by(bed_number = form.assign_bed.data).first()
        bed.patient_id = patient.identifying_number
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
    return render_template('patient.html', title='Patient info', patient=patient)


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
        patient.plan = form.plan.data
        patient.diagnosis = form.diagnosis.data
        current_bed = patient.location[0]
        current_bed.patient_id = None  # Set the old bed back to empty
        new_bed=Bed.query.filter_by(bed_number = form.assign_bed.data).first()
        new_bed.patient_id = patient.identifying_number # assign patient to new bed
        new_bed.user_id, current_bed.user_id = current_user.id, current_user.id
        db.session.commit()
        flash('Patient information updated successfuly', 'success')
        return redirect(url_for('patient', pn = patient.identifying_number))
    form.past_medical_history.data = patient.past_medical_history
    form.past_surgical_history.data = patient.past_surgical_history
    form.medications.data = patient.medications
    form.social_history.data = patient.social_history
    form.allergies.data = patient.allergies
    form.plan.data = patient.plan
    return render_template('edit.html', title='Edit patient info', form=form, patient=patient)


@app.route('/patient/<pn>/discharge', methods=['POST'])
@login_required
def discharge(pn):
    "Will allow user to remove a patient from the database"
    patient = Patient.query.filter_by(identifying_number = pn).first()
    Patient_jobs = Investigation.query.filter_by(patient_id = patient.id)
    bed = patient.location
    bed.patient_id = None
    db.session.delete(patient)
    db.session.delete(patient_jobs)
    db.session.commit()
    flash('Patient has been discharged', 'danger')
    return redirect(url_for('patient_list'))


@app.route('/job_list', methods=['GET', 'POST'])
@login_required
def job_list():
    "List all current jobs"
    jobs = Investigation.query.all()
    # users = User.query.all()
    # add ability to sort by user
    return render_template('job_list.html', title='Investigations', jobs=jobs)


@app.route('/my_jobs', methods=['GET', 'POST'])
@login_required
def my_jobs():
    "List all open jobs that are assigned to current user"
    task_list = Investigation.query.filter_by(assigned_to=current_user.id)
    return render_template('my_jobs.html', title='My Jobs', task_list=task_list)


@app.route('/job_list/<jn>/assign_job', methods=['GET', 'POST'])
@login_required
def assign_job(jn):
    job = Investigation.query.filter_by(id = jn).first()
    job.assigned_to = current_user.id
    db.session.commit()
    flash('Job has been assigned to you.', 'success')
    return redirect(url_for('job_list'))


@app.route('/patient/<pn>/add_job', methods=['POST'])
@login_required
def add_job(pn):
    patient = Patient.query.filter_by(identifying_number=pn).first()
    text =request.form['text']
    job = Investigation(task = text, patient_id=patient.id)
    db.session.add(job)
    db.session.commit()
    flash('Job added successfuly', 'success')
    return redirect(url_for('patient', pn = patient.identifying_number))@app.route('/patient/<pn>/add_job', methods=['POST'])

@app.route('/job_list/<jn>/advance_job', methods=['GET', 'POST'])
@login_required
def advance_job(jn):
    "Mark job as ordered if not ordered, and done if already ordered."
    job = Investigation.query.filter_by(id=jn).first()
    if job.ordered:
        job.done = True
    else:
        job.ordered = True
    db.session.commit()
    flash('Job updated successfuly', 'success')
    return redirect(url_for('my_jobs'))


@app.route('/job_list/<jn>/undo_advance_job', methods=['GET', 'POST'])
@login_required
def undo_advance_job(jn):
    "Mark job as not ordered if not ordered, and ordered if done."
    job = Investigation.query.filter_by(id=jn).first()
    if job.done:
        job.done = False
    else:
        job.ordered = False
    db.session.commit()
    flash('Job updated successfuly', 'success')
    return redirect(url_for('my_jobs'))


########################################  TODO  ###########################################################
# if job selected is already on somebody's list you should have a little modal warning before assignment
#
# Should be able to update the job list from the patient notes
# Add way to mark jobs as ordered and chased and maybe even a timeastamp and who it is assigned to.

