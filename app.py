# 
# Imports
#
import datetime
from types import DynamicClassAttribute
from flask import Flask, render_template, abort, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from qrcode.main import QRCode
from wtforms.meta import DefaultMeta
from forms import ImpfnachweisForm, LoginForm, AddVaccination, ScanQRForm

import qrcode
import pyqrcode
import json
import cv2
import ast
from PIL import Image
# from django.shortcuts import render
# import qrcode.image.svg
from io import BytesIO
from PIL import Image
import io
from io import StringIO
from base64 import b64encode
#import pyzbar.pyzbar
#
from pyzbar import pyzbar
#import pyzbar.pyzbar as pyzbar
#import numpy as np
from pyzbar.pyzbar import decode

# 
# Initialization of Flask Application
#

app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = 'test'



#
# DATABASE
#

#Location of the database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Start1210!@localhost:5432/vaccination_database'
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

    # if request.method == "POST":
    #     branch = Impfung.query.all()
        # return render_template('patient_vaccination_certificate.html', branch=branch)
    
    return render_template('patient/patient_vaccination_certificate.html')

@app.route("/patient/impfeintrag")
def patient_vaccination_entry():
    return render_template('patient/patient_vaccination_entry.html')

@app.route("/patient/impfeintrag/manuell", methods=['POST', 'GET'])
#@login_required
def addVaccination():

    form = AddVaccination()

    if form.validate_on_submit():

        unique_certificate_identifier = 1
        while Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first() is not None:
            unique_certificate_identifier = unique_certificate_identifier + 1

        #unique_patient_identifier ?
        new_vaccination = Proof_of_vaccination(unique_certificate_identifier=unique_certificate_identifier, date_of_vaccination = form.date_of_vaccination.data, vaccine = form.vaccine.data, batch_number=form.batch_number.data, vaccine_category=form.vaccine_category.data, unique_issuer_identifier=form.unique_issuer_identifier.data, disease= "/", vaccine_marketing_authorization_holder= "/", issued_at= "/")
        db.session.add(new_vaccination)
        db.session.commit()

        #flash('Impfeintrag erstellt!')
        #return redirect(url_for('patient_vaccination_certificate'))

    return render_template('patient/patient_vaccination_manual_entry.html', form=form)

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

@app.route("/patient/impfeintrag/scan",methods =["GET", "POST"])
def patient_scan():
    form = ScanQRForm()
    #form =ImpfnachweisForm()
    ### open camera
    cap = cv2.VideoCapture(0)
    while True:
        _,frame = cap.read() #### get next frame of the camera
        decodedObjects = pyzbar.decode(frame) # decode QR-Code 
        for objects in decodedObjects:
            bytstr = objects.data
            dictstr = bytstr.decode('utf-8')
            certificate_data = ast.literal_eval(dictstr)
            print(certificate_data)
        cv2.imshow('Impfnachweis einlesen',frame) # show the frame
        key = cv2.waitKey(1)
        if key ==27:
            break

        #add_certificate_data = Proof_of_vaccination(f_name =form.f_name.data, date_of_vaccination = form.date_of_vaccination.data, vaccine = form.vaccine.data, batch_number=form.batch_number.data, vaccine_category=form.vaccine_category.data, unique_issuer_identifier=form.unique_issuer_identifier.data, disease= "/", vaccine_marketing_authorization_holder= "/", issued_at= "/")
        #db.session.add(nadd_certificate_data)
        #db.session.commit()
    return render_template("/patient/patient_scan.html",form=form)

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

@app.route("/issuer/QR", methods =["GET", "POST"])   
def issuer_create_qr():
    form = ImpfnachweisForm()
    qr = {}
    img = []
    file_object = io.BytesIO()

## Clicking on the submit button is creating JSON-Object with input data
    if form.is_submitted():
        proof_of_vaccination= {}
        proof_of_vaccination['f_name']= form.f_name.data
        proof_of_vaccination['l_name'] = form.l_name.data
        proof_of_vaccination['date_of_birth']=form.date_of_birth.data
        proof_of_vaccination['date_of_vaccination'] = form.date_of_vaccination.data
        proof_of_vaccination['vaccination_category'] = form.vaccine_category.data
        proof_of_vaccination['vaccine_marketing_authorization_holder'] = form.vaccine_marketing_authorization_holder.data
        proof_of_vaccination['batch_number'] = form.batch_number.data
        proof_of_vaccination['issued_at'] = form.issued_at.data
        proof_of_vaccination['certificate_issuer'] = form.certificate_issuer.data
        
        qr = QRCode(version=1, box_size=6,border=4)
        qr.add_data(proof_of_vaccination)
        qr.make()
        #qr = qrcode.make(proof_of_vaccination)
        img = qr.make_image (fill = 'black', back_color = 'white')
        img.save(file_object,'PNG')
        

    return render_template("/issuer/issuer_create_qr.html", form=form, qr="data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii'))



@app.route("/login")
def login():
    return render_template("/login/login.html", title = 'Login', form=form)

@app.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():   
        if form.username.data == 'Patient1' and form.password.data =="Test":
            flash(f'Login erfolgreich für {form.username.data}', category = 'success')
            return redirect(url_for('patient_home'))
        if form.username.data == 'Issuer1' and form.password.data =="Test":
            return redirect(url_for('issuer_home'))
            
         #else:
            # flash(f'Login fehlgeschlagen für {form.username.data}', category = 'danger')
    return render_template("/login/login.html", title = 'Login', form=form)



# 
# Run application
#
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

