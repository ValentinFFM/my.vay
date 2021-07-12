from my_vay import db
from my_vay import loginManager
from flask_login import UserMixin
from flask import session

@loginManager.user_loader
def loadUser(user_id):
    if session['user_type'] == 'patient':
        return Patient.query.get(user_id)
    elif session['user_type'] == 'issuer':
        return Issuer.query.get(user_id)
    
# Patient Model
class Patient(db.Model, UserMixin):
    # Primary Key for patient is the username
    unique_patient_identifier = db.Column(db.Integer, primary_key = True)
    
    # Defining all required attributes
    password = db.Column(db.String, nullable = False)
    f_name = db.Column(db.String, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_birth = db.Column(db.Date, nullable = False)
    
    # Defining relationship to proof_of_vaccination
    proof_of_vaccination_identifier = db.relationship('Proof_of_vaccination', backref = 'patient') 
    
    # Defines the attribute that is given back, when the get_id function is called on an object of this class
    def get_id(self):
        return (self.unique_patient_identifier)

# Issuer Model
class Issuer(db.Model, UserMixin):
    # Defining primary key
    unique_issuer_identifier = db.Column(db.Integer, primary_key = True)
    
    # Defining all required attributes
    password = db.Column(db.String, nullable = False)
    f_name = db.Column(db.String, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_birth = db.Column(db.Date, nullable = False)
    
    # Defining relationship to proof_of_vaccination
    proof_of_vaccination_identifier = db.relationship('Proof_of_vaccination', backref = 'issuer') 

# Proof_of_vaccination Model
class Proof_of_vaccination(db.Model):
    # Defining primary key
    unique_certificate_identifier = db.Column(db.Integer, primary_key = True)
    
    # Defining all required attributes
    date_of_vaccination = db.Column(db.Date, nullable = False)
    vaccine_category = db.Column(db.String, nullable = False)
    disease = db.Column(db.String, nullable = False)
    vaccine = db.Column(db.String, nullable = False)
    vaccine_marketing_authorization_holder = db.Column(db.String, nullable = False)
    batch_number = db.Column(db.String, nullable = False)
    issued_at = db.Column(db.DateTime, nullable = False)
    
    # Defining relationship to patient
    unique_patient_identifier = db.Column(db.Integer, db.ForeignKey('patient.unique_patient_identifier'), nullable=False)
    
    # Defining relationship to issuer
    unique_issuer_identifier = db.Column(db.Integer, db.ForeignKey('issuer.unique_issuer_identifier'), nullable=False)
    
    db.Column(db.String, nullable = False)

# Create tables
db.create_all()