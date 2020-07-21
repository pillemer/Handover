from datetime import datetime
from handover import db, login_manager
from flask_login import UserMixin

# >>> from handover import db  -import the database to effect changes from the python terminal
# >>> db.create_all()          -to create the table in the models.py file and the db.
# >>> db.drop_all()            -to erase all tables in the database.
# >>> user_1 = User(username = '', password = '')  -to create a user
# >>> db.session.add(user_1)   -to add user to the db
# >>> db.session.commit()      -to commit all changes made to db
# >>> User.query.all()         -returns list of al entries to User
# >>> user = User.query.filer_by(username='').first()  -query database with filter
# >>> user = User.query.get(1)  -query database with id filter
# >>> user.id /.username /.password  -to access individual datum 

# TODO: Add a colum to the bed table with the ward information. then you can sort the beds by ward and even have two drop down selection when assigning beds. Ward then bed number.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    activity = db.relationship('Bed', backref='author', lazy=True)
    jobs = db.relationship('Investigation', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.Text, unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.identifying_number'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Bed('{self.bed_number}')"


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    presenting_complaint = db.Column(db.Text, nullable=False)
    past_medical_history = db.Column(db.Text)
    past_surgical_history = db.Column(db.Text)
    medications = db.Column(db.Text)
    social_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    plan = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    date_of_birth = db.Column(db.Text, nullable=False)
    identifying_number = db.Column(db.Text(20), nullable=False, unique=True) # URI or other hospital generated number
    location = db.relationship('Bed', backref='patient', lazy=True)
    investigations = db.relationship('Investigation', backref='subject', lazy=True)

    def __repr__(self):
        return f"""Patient('{self.presenting_complaint}', 
                        '{self.past_medical_history}', 
                        '{self.past_surgical_history}', 
                        '{self.medications}', 
                        '{self.social_history}', 
                        '{self.allergies}', 
                        '{self.plan}'
                        '{self.diagnosis}',
                        '{self.date_of_birth}', 
                        '{self.identifying_number}')"""


class Investigation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text)
    ordered = db.Column(db.Boolean, default=False)
    done = db.Column(db.Boolean, default=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __repr__(self):
        return f"Investigation('{self.task}', '{self.ordered}', '{self.done}', '{self.patient_id}', '{self.assigned_to}')"

