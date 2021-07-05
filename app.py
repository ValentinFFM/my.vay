# Imports from Flask

# Imports from Flask
from flask import Flask, render_template, abort
from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, DataRequired, Email
# from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__)


#
# DATABASE
#

# Location of the database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Master123@localhost:5432/vaccination_database'
app.config['SQLALCHEMY_ECHO'] = True

# Initializing database with SQLAlchemy
db = SQLAlchemy(app)

# Patient Model
class Patient(db.Model):
    # Primary Key for patient is the username
    unique_patient_identifier = db.Column(db.String, primary_key = True)
    
    # Defining all required attributes
    password = db.Column(db.String, nullable = False)
    f_name = db.Column(db.String, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_birth = db.Column(db.DateTime, nullable = False)
    
    # Defining relationship to proof_of_vaccination
    proof_of_vaccination_identifier = db.relationship('Proof_of_vaccination', backref = 'patient') 

# Issuer Model
class Issuer(db.Model):
    # Defining primary key
    unique_issuer_identifier = db.Column(db.String, primary_key = True)
    
    # Defining all required attributes
    password = db.Column(db.String, nullable = False)
    f_name = db.Column(db.String, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_birth = db.Column(db.DateTime, nullable = False)
    
    # Defining relationship to proof_of_vaccination
    proof_of_vaccination_identifier = db.relationship('Proof_of_vaccination', backref = 'issuer') 

# Proof_of_vaccination Model
class Proof_of_vaccination(db.Model):
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
    
    # Defining relationship to patient
    unique_patient_identifier = db.Column(db.String, db.ForeignKey('patient.unique_patient_identifier'), nullable=False)
    
    # Defining relationship to issuer
    unique_issuer_identifier = db.Column(db.String, db.ForeignKey('issuer.unique_issuer_identifier'), nullable=False)
    
    db.Column(db.String, nullable = False)

# Create tables
db.create_all()


#
# Routing
#

# Landing Page route
@app.route("/")
def home():
    return render_template("landing.html")

# Impdaten anzeigen

@app.route("/patient")
def patient_home():

# EXAMPLE CODE: Creating new user
    # birth_date = datetime.datetime(2020,5,17)
    # new_patient = Patient(unique_patient_identifier = "12345678", password = "football4life", f_name="Valentin", l_name="Müller", date_of_birth=birth_date)
    # db.session.add(new_patient)
    # db.session.commit()

    # if request.method == "POST":
    #     branch = Impfung.query.all()
        # return render_template('patient_vaccination_certificate.html', branch=branch)
    print(vaccination)
    return render_template('patient/patient_vaccination_certificate.html', vaccination=vaccination)

@app.route("/patient/impfeintrag-neu")
def patient_vaccination_entry():
    return render_template('patient/patient_vaccination_entry.html')


# @app.route('/showvaccination', methods=['POST'])
# def showvaccination():
#     if request.method == "POST":
#         branch = Impfung.query.all()
#         return render_template('patient_vaccination_certificate.html', branch=branch)

#Neuer manueller Impfeintrag

# @app.route('/addvaccination', methods=['POST'])
# def addvaccination():
#     if request.method == "POST":
#         Impfdatum = request.form['Impfdatum']
#         Impfstoff = request.form['Impfstoff']
#         Chargennummer = request.form['Chargennummer']
#         Impfkategorie = request.form['Impfkategorie']
#         Medizinische_Einrichtung = request.form['Medizinische_Einrichtung']
#         state_ = request.form['state_']
#         data = Impfung(Impfdatum, Impfstoff, Chargennummer, Impfkategorie, Medizinische_Einrichtung)
#         db.session.add(data)
#         db.session.commit()
#         branch = Impfung.query.all()
#         return render_template('patient_vaccination_certificate.html', branch = branch)


    
    

@app.route("/patient/impfwissen")
def patient_impfwissen():
    return render_template("/patient/patient_vaccination_knowledge.html")

@app.route("/patient/kalender")
def patient_kalender():
    return render_template("/patient/patient_calendar.html")

@app.route("/patient/scan")
def patient_scan():
    return render_template("/patient/patient_scan.html")

@app.route("/patient/profil")
def patient_profil():
    return render_template("/patient/patient_profile.html")

# Issuer routes
@app.route("/issuer")
def issuer_home():
    return render_template("/issuer/issuer_create_qr.html")

@app.route("/issuer/impfwissen")   
def issuer_impfwissen():
    return render_template("issuer/issuer_vaccination_knowledge.html")

@app.route("/issuer/profil")
def issuer_profil():
    return render_template("/issuer/issuer_profile.html")

@app.route("/QR", methods =["GET", "POST"])   
def issuer_create_qr():
    #fields = NONE
    form = ImpfnachweisForm()
    return render_template("issuer_create_qr.html", title = "Impfnachweis erstellen",form=form)

# 
# Run application
#
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

