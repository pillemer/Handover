# some helpful functions for the website

from Handover import db
from Handover.models import User, Patient, Bed
from flask import flash

# helper function to popluate the dropdown list of beds for each patient
def bed_choices(pn=None):   
    if pn != None:
        patient= Patient.query.filter_by(identifying_number=pn).first()
        current_bed = patient.location[0]  # bed currently assigned to patient
        choices=[(current_bed.bed_number, current_bed.bed_number)]
    else:
        choices = []
    available_beds = Bed.query.filter_by(patient_id=None).all()  # all unassigned beds
    for bed in available_beds:
        choices.append((bed.bed_number, bed.bed_number))
    return choices

# helper function to print out form errors. This should be not be in use anywehre when the app is live.
def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')