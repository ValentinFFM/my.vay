# 
# Imports
#
from my_vay import app, db

# General imports for Flask
from flask import Flask, render_template, abort, url_for, redirect, flash, request, session

# Imports for forms
from my_vay.forms import ImpfnachweisForm, PatientLoginForm, AddVaccination, PatientRegistrationForm, IssuerRegistrationForm, IssuerLoginForm

# Imports for user handeling
from flask_login import login_user, current_user, logout_user, login_required, UserMixin, LoginManager

from my_vay.models import Patient, Issuer, Proof_of_vaccination

from base64 import b64encode



#
# Gerneral routes
#

# Landing page route
@app.route("/")
def home():
    return render_template("landing.html")

# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for('home'))



#
# Patient routes
#

# Patient - Landing page route
@app.route("/patient")
@login_required
def patient_home():

    # if request.method == "POST":
    #     branch = Impfung.query.all()
        # return render_template('patient_vaccination_certificate.html', branch=branch)
    
    return render_template('patient/patient_vaccination_certificate.html')

# Patient - Login route
@app.route("/patient/login", methods =["GET", "POST"])
def patient_login():
    
    # Redirects user to the patient landing page, if he is already signed in
    if current_user.is_authenticated:
        if session['user_type'] == 'patient':
            return redirect(url_for('patient_home'))
    
    # Loads the PatientLoginForm from forms.py 
    form = PatientLoginForm()
    
    # If the form is submitted and validated then...
    if form.validate_on_submit():
        
        # Database is queryed based on the unique_patient_identifier
        patient = Patient.query.filter_by(unique_patient_identifier=form.unique_patient_identifier.data).first()
        
        # If a patient with the entered unique_patient_identifier exists and the password in the database is the same as in the form then...
        if patient and patient.password == form.password.data:
            
            # Patient is written into a cookie and user is logged in
            session['user_type'] = 'patient'
            login_user(patient, remember=form.remember.data)
            
            # Patient is redirected to the patient landing page
            return redirect(url_for('patient_home'))
    
    return render_template('patient/patient_login.html', form=form)

# Patient - Registration route
@app.route("/patient/registrierung", methods =["GET", "POST"])
def patient_registration():
    form = PatientRegistrationForm()
    
    if form.validate_on_submit():
        new_patient = Patient(f_name=form.f_name.data, l_name=form.l_name.data, date_of_birth=form.date_of_birth.data, unique_patient_identifier=form.unique_patient_identifier.data, password=form.password.data)
        db.session.add(new_patient)
        db.session.commit()
        
        return redirect(url_for('patient_login'))
    
    return render_template('patient/patient_registration.html', form=form)

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

@app.route("/patient/impfwissen")
def patient_impfwissen():
    return render_template("/patient/patient_vaccination_knowledge.html")

@app.route("/patient/kalender")
def patient_kalender():
    return render_template("/patient/patient_calendar.html")

@app.route("/patient/impfeintrag/scan")
def patient_scan():
    #img = cv2.imread('Beispiel.png')
    #cv2.imshow('Ihr Impfnachweis',img)
    #print(decode(img))

    return render_template("/patient/patient_scan.html")

@app.route("/patient/profil")
def patient_profil():
    return render_template("/patient/patient_profile.html")



# 
# Issuer routes
#

# Landing page route
@app.route("/issuer")
def issuer_home():
    return render_template("/issuer/issuer_create_qr.html")

# Login route
@app.route("/issuer/login", methods =["GET", "POST"])
def issuer_login():
    
    if current_user.is_authenticated:
        return redirect(url_for('patient_home'))
    
    form = IssuerLoginForm()
    
    if form.validate_on_submit():
        patient = Patient.query.filter_by(unique_patient_identifier=form.unique_patient_identifier.data).first()
        
        if patient:
            session['user_type'] = 'patient'
            login_user(patient, remember=form.remember.data)

            return redirect(url_for('patient_home'))
    
    return render_template('issuer/issuer_login.html', form=form)

# Registration route
@app.route("/issuer/registrierung", methods =["GET", "POST"])
def issuer_registration():
    form = IssuerRegistrationForm()
    
    if form.validate_on_submit():
        new_issuer = Issuer(f_name=form.f_name.data, l_name=form.l_name.data, date_of_birth=form.date_of_birth.data, unique_issuer_identifier=form.unique_patient_identifier.data, password=form.password.data)
        db.session.add(new_issuer)
        db.session.commit()
        
        return redirect(url_for('issuer_login'))
    
    return render_template('issuer/issuer_registration.html', form=form)

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