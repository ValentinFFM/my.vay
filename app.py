# Imports from Flask
import numpy as np
from types import DynamicClassAttribute
from flask import Flask, render_template, abort, url_for, redirect, flash
from qrcode.main import QRCode
from wtforms.meta import DefaultMeta
from forms import ImpfnachweisForm, LoginForm
from flask_sqlalchemy import SQLAlchemy


import qrcode
import pyqrcode
import json
#import cv2

from PIL import Image
from django.shortcuts import render
import qrcode.image.svg
from io import BytesIO
from PIL import Image
import io
from io import StringIO
from base64 import b64encode


# Initialize flask application
app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = 'test'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Master123@localhost:5432/vaccination_database'
#app.config['SQLALCHEMY_ECHO'] = True

@app.route("/")
def home():
    return render_template("landing.html")

# Patient routes
@app.route("/patient")
def patient_home():
    return render_template("/patient/patient_vaccination_certificate.html")

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
        
        qr = QRCode(version=1, box_size=6,border=5)
        qr.add_data(proof_of_vaccination)
        qr.make()
        #qr = qrcode.make(proof_of_vaccination)
        img = qr.make_image (fill = 'black', back_color = 'white')
        #img = np.array(img)
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



# Run application with debug console
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

