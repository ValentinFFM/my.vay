# Imports from Flask
from types import DynamicClassAttribute
from flask import Flask, render_template, abort, url_for, redirect, flash
from wtforms.meta import DefaultMeta
from forms import ImpfnachweisForm, LoginForm

import pyqrcode
import qrcode
import png
import cv2


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
    #fields = NONE
    form = ImpfnachweisForm()
    if form.validate_on_submit():
        impfnachweis = ImpfnachweisForm(
            Vorname = form.f_name.data,
            Nachname = form.l_name.data,
            Geburtsdatum = form.date_of_birth.data,
            Impfdatum = form.date_of_vaccination.data,
            Impfkategorie = form.vaccine_category.data,
            Krankheit = form.disease.data,
            Impfstoff = form.vaccine.data,
            Hersteller = form.vaccine_marketing_authorization_holder.data,
            Chargennummer = form.batch_number.data,
            Ausstellungszeitpunkt = form.issued_at.data,
            Arztkennung = form.certificate_issuer.data)
        impfnachweis.save()
        qr = qrcode.make()
        qr.save('PrototypischerImpfnachweis.png')
        qr.show()
        return redirect(url_for('home'))
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

