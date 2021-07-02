from app import db

class Patient(db.Model):
    # Primary Key for patient is the username
    username = db.Column(db.String, primary_key = True)
    password = db.Column(db.String, nullable = False)
    f_name = db.Column(db.Sting, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_birth = db.Column(db.DateTime, nullable = False)
    
    # Defining relationship to proof_of_vaccination
    #proof_of_vaccination_ = 
    

class Issuer(db.Model):
    # Defining primary key
    username = db.Column(db.Column, primary_key = True)
    
    # Defining all required attributes
    password = db.Column(db.String, nullable = False)
    f_name = db.Column(db.Sting, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_birth = db.Column(db.DateTime, nullable = False)
    
class proof_of_vaccination(db.Model):
    # Defining primary key
    unique_certificate_identifier = db.Column(db.String, primary_key = True)
    
    # Defining all required attributes
    date_of_vaccination = db.Column(db.DateTime, nullable = False)
    vaccine_category = db.Column(db.String, nullable = False)
    disease = db.Column(db.String, nullable = False)
    vaccine = db.Column(db.String, nullable = False)
    vaccine_marketing_authorization_holder = db.Column(db.String, nullable = False)
    batch_number = db.Column(db.String, nullable = False)
    issued_at = db.Column(db.DateTime, nullable = False)
    certificate_issuer = db.Column(db.String, nullable = False)
    
    # Defining relationship to patient
    patient_username = db.Column(db.String, db.ForeignKey('patient.username'), nullable=False)