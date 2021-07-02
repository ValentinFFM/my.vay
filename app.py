# Imports from Flask
from types import DynamicClassAttribute
from flask import Flask, render_template, abort, url_for, redirect, flash
from wtforms.meta import DefaultMeta
from forms import ImpfnachweisForm, LoginForm

import pyqrcode
import qrcode
#import png
#import cv2


# Initialize flask application
app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = 'test'



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
    ## Clicking on the submit button is creating JSON-Object
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
        ###Create QR Code with data of JSON-Object
        qr = qrcode.make(proof_of_vaccination)
        #qr.save('PrototypischerImpfnachweis.png')
        ### display QR Code
        qr.show()
       #return redirect(url_for('show_qr', qr=qr))
    return render_template("/issuer/issuer_create_qr.html", form=form)




@app.route("/login")
def login():

    form = LoginForm()
    if form.validate_on_submit():   
        if form.username.data == 'Arzt' and form.password.data =="Test":
            flash(f'Login erfolgreich für {form.username.data}', category = 'success')
            return redirect(url_for('home'))
         #else:
            # flash(f'Login fehlgeschlagen für {form.username.data}', category = 'danger')
    return render_template("/login/login.html", title = 'Login', form=form)



# Run application with debug console
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

