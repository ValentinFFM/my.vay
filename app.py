# 
# Imports
#
import datetime
from types import DynamicClassAttribute, new_class
from flask import Flask, render_template, abort, url_for, redirect, flash, request, Response
from flask_sqlalchemy import SQLAlchemy
from qrcode.main import QRCode
from werkzeug.exceptions import default_exceptions
import wtforms
from wtforms.meta import DefaultMeta
from forms import ImpfnachweisForm, LoginForm, AddVaccination, ScanQRForm, CheckQRForm
import sys

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
import uuid
#import pyzbar.pyzbar
#
from pyzbar import pyzbar
#import pyzbar.pyzbar as pyzbar
#import numpy as np
from pyzbar.pyzbar import _decode_symbols, decode

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
    date_of_birth = db.Column(db.Date, nullable = False)
    
    # Defining relationship to proof_of_vaccination
    proof_of_vaccination_identifier = db.relationship('Proof_of_vaccination', backref = 'issuer') 

# Proof_of_vaccination Model
class Proof_of_vaccination(db.Model):
    # Defining primary key
    
    unique_certificate_identifier = db.Column(db.String, primary_key = True)
   
  
    
    # Defining all required attributes
    f_name = db.Column(db.String, nullable = False)
    l_name = db.Column(db.String, nullable = False)
    date_of_vaccination = db.Column(db.Date, nullable = False)
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
    return render_template('patient/patient_vaccination_certificate.html')

@app.route("/patient/impfeintrag")
def patient_vaccination_entry():
    return render_template('patient/patient_vaccination_entry.html')

@app.route("/patient/impfeintrag/manuell", methods=['POST', 'GET'])
#@login_required
def addVaccination():
    form = AddVaccination()
    new_vaccination = {}
    if form.validate_on_submit():
        #unique_certificate_identifier = 1
        #while Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first() is not None:
         #   unique_certificate_identifier = unique_certificate_identifier + 1
        #unique_patient_identifier ?
        new_vaccination = Proof_of_vaccination(unique_certificate_identifier='1', date_of_vaccination = form.date_of_vaccination.data, vaccine = form.vaccine.data, batch_number=form.batch_number.data, vaccine_category=form.vaccine_category.data, unique_issuer_identifier=form.unique_issuer_identifier.data, disease= "/", vaccine_marketing_authorization_holder= "/", issued_at= "/")
        db.session.add(new_vaccination)
        db.session.commit()

        #flash('Impfeintrag erstellt!')
        #return redirect(url_for('patient_vaccination_certificate'))

    return render_template('patient/patient_vaccination_manual_entry.html', form=form)


@app.route("/patient/impfwissen")
def patient_impfwissen():
        return render_template("/patient/patient_vaccination_knowledge.html")

@app.route("/patient/kalender")
def patient_kalender():
    return render_template("/patient/patient_calendar.html")






















def gen_frames():
        camera = cv2.VideoCapture(0)
        
        
        while True:
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                QRidentified = decode(frame)
                if QRidentified == True:
                    break
                    #return redirect (url_for('checkQR', vaccination_data = vaccination_JSON))

                #print(vaccination_JSON)
               
                    #return redirect (url_for('checkQR', vaccination_data = vaccination_JSON)) # ab dem Redirect hängt es
                
                else:   
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_buffer = buffer.tobytes()
                    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n') 
                             
def decode(frame):
    decodedObject = pyzbar.decode(frame) # decode QR-Code
    if decodedObject:
        print (decodedObject, file=sys.stderr)
        return True

        
        
@app.route("/patient/impfeintrag/scan",methods =["GET", "POST"])
def patient_scan():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/patient/impfeintrag/checkQR",methods =["GET", "POST"])
def checkQR(vaccination_data):
    form = CheckQRForm()
    form.f_name.default = vaccination_data['f_name']
    form.l_name.default = vaccination_data['l_name']
    form.date_of_birth.default = vaccination_data['date_of_birth']
    form.date_of_vaccination.default = vaccination_data['date_of_vaccination']
    form.vaccine_category.default = vaccination_data['vaccine_category']
    form.disease.default = vaccination_data['disease']
    form.vaccine_marketing_authorization_holder.default = vaccination_data['vaccine_marketing_authorization_holder']
    form.batch_number.default = vaccination_data['batch_number']
    form.issued_at.default = vaccination_data['issued_at']
    form.unique_issuer_identifier.default = vaccination_data['unique_issuer_identifier']
    form.unique_certificate_identifier.default = vaccination_data['unique_certificate_identifier']

    if form.validate_on_submit():
        new_entry = Proof_of_vaccination(unique_certificate_identifier = vaccination_data['unique_certificate_identifier'], f_name =vaccination_data['f_name'], l_name = vaccination_data['l_name'], date_of_vaccination = vaccination_data['date_of_vaccination'], vaccine = vaccination_data['vaccine'], batch_number=vaccination_data['batch_number'], vaccine_category=vaccination_data['vaccine_category'], unique_issuer_identifier=vaccination_data['uniqe_certificate_identifier'], disease= vaccination_data['disease'], vaccine_marketing_authorization_holder= vaccination_data['vaccine_marketing_authorization_holder'], issued_at= vaccination_data['issued_at'])
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('patient_home'))
    return render_template("/patient/patient_checkQR.html", form=form)




































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
## Clicking on the submit button is creating with input data
    if form.is_submitted():
        proof_of_vaccination= {}
        proof_of_vaccination['f_name']= form.f_name.data
        proof_of_vaccination['l_name'] = form.l_name.data
        proof_of_vaccination['date_of_birth']=form.date_of_birth.data
        proof_of_vaccination['date_of_vaccination'] = form.date_of_vaccination.data
        proof_of_vaccination['vaccine_category'] = form.vaccine_category.data
        proof_of_vaccination['disease'] = form.disease.data
        proof_of_vaccination['vaccine'] = form.vaccine.data
        proof_of_vaccination['vaccine_marketing_authorization_holder'] = form.vaccine_marketing_authorization_holder.data
        proof_of_vaccination['batch_number'] = form.batch_number.data
        proof_of_vaccination['issued_at'] = form.issued_at.data
        proof_of_vaccination['unique_issuer_identifier'] = form.unique_issuer_identifier.data
        proof_of_vaccination['unique_certificate_identifier'] = '1'
        qr = QRCode(version=1, box_size=3,border=3)
        qr.add_data(proof_of_vaccination)
        qr.make()
        #qr = qrcode.make(proof_of_vaccination)
        img = qr.make_image (fill = 'black', back_color = 'white')
        img.save(file_object,'PNG')
    
    return render_template("/issuer/issuer_create_qr.html", form=form, qr="data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii'))



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

