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
    vaccine = db.Column(db.String, nullable = False)
    vaccine_marketing_authorization_holder = db.Column(db.String, nullable = False)
    batch_number = db.Column(db.String, nullable = False)
    issued_at = db.Column(db.DateTime, nullable = False)
    
    # Defining relationship to patient
    unique_patient_identifier = db.Column(db.Integer, db.ForeignKey('patient.unique_patient_identifier'), nullable = False)
    
    # Defining relationship to issuer
    unique_issuer_identifier = db.Column(db.Integer, db.ForeignKey('issuer.unique_issuer_identifier'), nullable = False)
    
    # Defining relationship to vaccination
    vaccination_id = db.Column(db.Integer, db.ForeignKey('vaccination.vaccination_id'), nullable = False)


class Vaccination(db.Model):
    
    vaccination_id = db.Column(db.Integer, nullable = False, primary_key = True)
    disease = db.Column(db.String, nullable = False)
    vaccine_category = db.Column(db.String(2), nullable = False)
    beginn_age = db.Column(db.Integer, nullable = False)
    end_age = db.Column(db.Integer)
    distance_to_pre_vaccination = db.Column(db.Integer)
    
    next_vaccination_id = db.Column(db.Integer, db.ForeignKey('vaccination.vaccination_id'))
    last_vaccination_id = db.relationship('Vaccination', backref = 'vaccination', uselist = False, remote_side=[vaccination_id]) 
    
    # Defining relationship to proof of vaccinations
    proof_of_vaccinations = db.relationship('Proof_of_vaccination', backref = 'vaccination') 

# Create tables
db.create_all()

# try:
#     vaccination_1 = Vaccination(vaccination_id = 7, disease = 'Pneumokokken', vaccine_category = 'S', beginn_age = 720, next_vaccination_id = 7)
#     vaccination_2 = Vaccination(vaccination_id = 6, disease = 'Pneumokokken', vaccine_category = 'G3', beginn_age = 11, end_age = 23,  next_vaccination_id = 7, distance_to_pre_vaccination = 6)
#     vaccination_3 = Vaccination(vaccination_id = 5, disease = 'Pneumokokken', vaccine_category = 'G2', beginn_age = 4, end_age = 23,  next_vaccination_id = 6)
#     vaccination_4 = Vaccination(vaccination_id = 4, disease = 'Pneumokokken', vaccine_category = 'G1', beginn_age = 2, end_age = 23,  next_vaccination_id = 5)
#     vaccination_5 = Vaccination(vaccination_id = 3, disease = 'Hepatitis B', vaccine_category = 'G3', beginn_age = 11, end_age = 204, distance_to_pre_vaccination = 6)
#     vaccination_6 = Vaccination(vaccination_id = 2, disease = 'Hepatitis B', vaccine_category = 'G2', beginn_age = 4, end_age = 204, next_vaccination_id = 3)
#     vaccination_7 = Vaccination(vaccination_id = 1, disease = 'Hepatitis B', vaccine_category = 'G1', beginn_age = 2, end_age = 204, next_vaccination_id = 2)

#     issuer_1 = Issuer(unique_issuer_identifier = 1, password = 'fussball', f_name = 'Max', l_name = 'Mustermann', date_of_birth = '1980-08-19')
#     issuer_2 = Issuer(unique_issuer_identifier = 2, password = '12345678', f_name = 'Marie', l_name = 'Musterfrau', date_of_birth = '1965-05-28')

#     patient_1 = Patient(unique_patient_identifier = 1, password = 'auto1234', f_name = 'Leon', l_name = 'Frank', date_of_birth = '2021-02-16')
#     patient_2 = Patient(unique_patient_identifier = 2, password = '12345678', f_name = 'Susi', l_name = 'Meier', date_of_birth = '1956-05-16')

#     proof_of_vaccination_1 = Proof_of_vaccination(unique_certificate_identifier = 1, date_of_vaccination = '2021-04-19', vaccine = 'Hepatitis B Impfstoff', vaccine_marketing_authorization_holder = 'Pfizer', batch_number='1234', issued_at = '2021-04-19', unique_patient_identifier = 1, unique_issuer_identifier = 1, vaccination_id = 1)
#     proof_of_vaccination_2 = Proof_of_vaccination(unique_certificate_identifier = 2, date_of_vaccination = '2021-06-19', vaccine = 'Hepatitis B Impfstoff', vaccine_marketing_authorization_holder = 'Pfizer', batch_number='4567', issued_at = '2021-06-19', unique_patient_identifier = 1, unique_issuer_identifier = 1, vaccination_id = 2)

#     db.session.add_all([vaccination_1, vaccination_2, vaccination_3, vaccination_4, vaccination_5, vaccination_6, vaccination_7, issuer_1, issuer_2, patient_1, patient_2, proof_of_vaccination_1, proof_of_vaccination_2])

#     db.session.commit()
# except:
#     print("Default data already entered")
