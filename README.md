# Handover
A webapp for medical staff on wards to efficiently handle their jobs and patient management.

To create the database and create the tables:

in python:
>>> from handover import db
>>> db.create_all()

( The database still needs to be initialized with some beds. Just the bed number is required.)
>>> from handover.models import Bed
>>> bed_1 = Bed(bed_number='1')
>>> db.session.add(bed_1)
>>> db.session.commit()
