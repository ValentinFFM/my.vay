# 
# Imports
#
from werkzeug.exceptions import PreconditionRequired
from my_vay import app, db

# General imports for Flask
from flask import Flask, render_template, abort, url_for, redirect, flash, request, session

# Imports for forms
from my_vay.forms import AddSideeffects, ImpfnachweisForm, PatientLoginForm, AddVaccination, PatientRegistrationForm, IssuerRegistrationForm, IssuerLoginForm, IssuerUpdateForm, PatientUpdateForm, ScanQRForm, SearchVaccine

# Imports for user handeling
from flask_login import login_user, current_user, logout_user, login_required, UserMixin, LoginManager

from my_vay.models import Patient, Issuer, Proof_of_vaccination, Vaccination, Sideeffects

from base64 import b64encode
import io
from qrcode.main import QRCode
import cv2
import ast
import sys

from datetime import datetime, date, timedelta
from dateutil import relativedelta



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


def check_for_vac_notifications():
    # Returns the proof_of_vaccinations of the logged-in-user from the database
    list_of_proof_of_vaccinations = Proof_of_vaccination.query.filter_by(unique_patient_identifier=current_user.unique_patient_identifier).all()
    
    notifications = []
    
    # Iterates through the proof_of_vaccinations
    for entry_in_proof_of_vaccinations in list_of_proof_of_vaccinations:
        
        # Returns the associated vaccination from proof_of_vaccinations
        associated_entry_in_vaccination = Vaccination.query.get(entry_in_proof_of_vaccinations.vaccination_id)
        next_vaccination_id = associated_entry_in_vaccination.next_vaccination_id
        
        notification_dict = {
            "next_vaccination_possible" : False,
            "next_vaccination_not_exisisting" : False,
            "beginn_age_reached": False,
            "end_age_not_reached": False,
            "dist_between_current_and_next_correct": False
        }
        
        # If this vaccination has a following vaccination...
        if next_vaccination_id:
            notification_dict["next_vaccination_possible"] = True
            
            #... then it's checked, if the following vaccination is missing.
            next_vaccination_already_existing = Proof_of_vaccination.query.filter_by(vaccination_id=next_vaccination_id).first()
            
            if next_vaccination_already_existing is None:
                notification_dict["next_vaccination_not_exisisting"] = True
                
                # Date of birth from current_user and today's date is detected
                user_date_of_birth = current_user.date_of_birth
                date_today = date.today()
                
                print("user_date_of_birth: " + str(type(user_date_of_birth)), file=sys.stderr)
                print("date_today: " + str(type(date_today)), file=sys.stderr)
                
                # Calculate difference in months between date_of_birth and today (Age in months)
                age = relativedelta.relativedelta(date_today, user_date_of_birth)
                age_in_months = age.months + age.years * 12
                
                # Returns the next vaccination from database
                next_vaccination = Vaccination.query.get(next_vaccination_id)
                
                # Beginn_age, end_age and distance to previous vaccination are read-out
                next_vaccination_beginn_age = next_vaccination.beginn_age
                next_vaccination_end_age = next_vaccination.end_age
                next_vaccination_dist_to_pre_vac = next_vaccination.distance_to_pre_vaccination
                
                if next_vaccination_beginn_age:
                    if age_in_months >= next_vaccination_beginn_age:
                        notification_dict["beginn_age_reached"] = True
                    else:
                        notification_dict["beginn_age_reached"] = False
                else:
                    notification_dict["beginn_age_reached"] = True

                if next_vaccination_end_age:
                    if age_in_months <= next_vaccination_end_age:
                        notification_dict["end_age_not_reached"] = True
                    else:
                        notification_dict["end_age_not_reached"] = False
                else:
                    notification_dict["end_age_not_reached"] = True
                
                if next_vaccination_dist_to_pre_vac:
        
                    date_of_current_vac = entry_in_proof_of_vaccinations.date_of_vaccination
                    dist_between_current_and_next_vac = relativedelta.relativedelta(date_today, date_of_current_vac)
                    dist_between_current_and_next_vac_in_months = dist_between_current_and_next_vac.months + dist_between_current_and_next_vac.years * 12
                        
                    if next_vaccination_dist_to_pre_vac <=  dist_between_current_and_next_vac_in_months:
                        notification_dict["dist_between_current_and_next_correct"] = True
                    else:
                        notification_dict["dist_between_current_and_next_correct"] = False
                else:
                    notification_dict["dist_between_current_and_next_correct"] = True
            else:
                notification_dict["next_vaccination_not_exisisting"] = False
        else:
            notification_dict["next_vaccination_possible"] = False
            
        if notification_dict["beginn_age_reached"] == True and notification_dict["end_age_not_reached"] == True and notification_dict["dist_between_current_and_next_correct"] == True and notification_dict["next_vaccination_not_exisisting"] == True and notification_dict["next_vaccination_possible"] == True:
            
            notification = {
                "disease" : next_vaccination.disease,
                "current_unique_certificate_identifier" : entry_in_proof_of_vaccinations.unique_certificate_identifier,
                "current_date_of_vaccination": entry_in_proof_of_vaccinations.date_of_vaccination,
                "current_vaccine_category" : associated_entry_in_vaccination.vaccine_category,
                "next_vaccine_category" : next_vaccination.vaccine_category
            }
            
            notifications.append(notification)
    
    return notifications
        
    

# @app.route("/test")
# def test_route():
#     notifications = check_for_vac_notifications()
#     print(notifications)
#     return render_template('html_container.html')
    

# Patient - Landing page route
@app.route("/patient",methods=['POST', 'GET'])
@app.route("/patient/<string:sort>", methods=['POST', 'GET'])
@app.route("/patient/<string:sort>/<string:search>", methods=['POST', 'GET'])
@login_required
def patient_home(sort='date', search=''):
    from datetime import date
    page = request.args.get('page', 1, type=int)
    form = SearchVaccine()
    vaccine_search = False
    today = 0
    test=0
    list1=[]
    sorting = []
    
    

    # Checks if a search term is used. If yes then patients first and last name are searched for the search term. Otherwise all patients of the doctor are executed
    if search:
        vaccine_search = True
        search = '%' + search + '%'
        branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).filter(Proof_of_vaccination.vaccine.like(search)).paginate(page=page, per_page=5)
        vaccination = Vaccination.query.filter(Proof_of_vaccination.vaccination_id == Vaccination.vaccination_id).all()
    else: 
        # Depending on an argument in the url, the patients are sorted in different ways.
        if sort == 'date':
            branch = Proof_of_vaccination.query.filter_by(unique_patient_identifier=current_user.unique_patient_identifier).order_by(Proof_of_vaccination.date_of_vaccination.desc()).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Proof_of_vaccination.vaccination_id == Vaccination.vaccination_id).all()
            sf_show = Proof_of_vaccination.query.filter_by(unique_patient_identifier=current_user.unique_patient_identifier).all()
            test = Sideeffects.query.all()
            today = date.today()
            for i in range (1):
                 today-= timedelta(days=1)
            today = today.strftime('%Y-%m-%d')
            print(today)

            for entry in sf_show:
                classifier= False
                print(entry)
                print('no')
                if entry.date_of_vaccination.strftime('%Y-%m-%d') == today:
                    print('geht')
                    for val in test:
                            if entry.unique_certificate_identifier == val.unique_certificate_identifier:
                                print('bricht ab')
                                classifier = True
                                break
                    if classifier == False:
                        list1.append(entry)
                        print('yes')
                    
                
            
            print(list1)
            
            
        elif sort == 'Pneumokokken':
            branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Vaccination.disease == sort).all()
        
            
            
        elif sort == 'Hepatitis B':
            branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Vaccination.disease == sort).all()
            print('test')
          
        else:
            abort(404)

    # If the validation is correct, then a flash message is displayed and the user is redirected to the login page.
    if form.is_submitted():
        return redirect(url_for('patient_home', sort='date', search=form.name.data))
    
    vac_notifications = check_for_vac_notifications()

    return render_template('patient/patient_vaccination_certificate.html', branch=branch, sort=sort, form=form, search=vaccine_search, vac_notifications=vac_notifications, list1=list1, vaccination=vaccination)

@app.route("/patient/sideeffects/<int:unique_certificate_identifier>", methods=['POST', 'GET'])
def new_sideeffect(unique_certificate_identifier):
    branch = Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first()

    form = AddSideeffects()
    
    # If the form is submitted and validated then...
    if form.is_submitted():
        unique_entry_identifier = 1
        while Sideeffects.query.filter_by(unique_entry_identifier=unique_entry_identifier).first() is not None:
            unique_entry_identifier = unique_entry_identifier + 1
        # a new patient is added to the database
        new_sideeffects = Sideeffects(unique_entry_identifier=unique_entry_identifier, unique_certificate_identifier=unique_certificate_identifier ,headache=form.headache.data, arm_hurts=form.arm_hurts.data, rash=form.rash.data, fever=form.fever.data, tummyache=form.tummyache.data, sideeffects=form.sideeffects.data)
        db.session.add(new_sideeffects)
        db.session.commit()
        
        return redirect(url_for('patient_home'))
    
    return render_template('patient/patient_sideeffects.html', branch = branch, form=form )

@app.route("/patientQR/<int:unique_certificate_identifier>", methods=['POST', 'GET'])
def open_QR(unique_certificate_identifier):
    branch = Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first()
    vaccination = Vaccination.query.filter(Proof_of_vaccination.vaccination_id == Vaccination.vaccination_id).first()

    qr = {}
    img = []
    file_object = io.BytesIO()

    proof_of_vaccination= {}
    proof_of_vaccination['unique_certificate_identifier']= branch.unique_certificate_identifier
    proof_of_vaccination['date_of_vaccination']= branch.date_of_vaccination
    proof_of_vaccination['vaccine']= branch.vaccine
    proof_of_vaccination['vaccination_id'] = branch.vaccination_id
    proof_of_vaccination['vaccine_marketing_authorization_holder']= branch.vaccine_marketing_authorization_holder
    proof_of_vaccination['batch_number']= branch.batch_number
    proof_of_vaccination['issued_at']= branch.issued_at
    proof_of_vaccination['unique_patient_identifier']= branch.unique_patient_identifier
    proof_of_vaccination['unique_issuer_identifier']= branch.unique_issuer_identifier

    print(proof_of_vaccination)

    qr = QRCode(version=1, box_size=6,border=4)
    qr.add_data(proof_of_vaccination)
    qr.make()
        #qr = qrcode.make(proof_of_vaccination)
    img = qr.make_image (fill = 'black', back_color = 'white')
    img.save(file_object,'PNG')

    return render_template('patient/patient_show_QR.html', branch = branch, vaccination=vaccination, qr="data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii'))


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

        else:
            flash('Es existiert kein Patient mit dieser Nutzer ID!', 'danger')
            return redirect(url_for('patient_login'))
    
    return render_template('patient/patient_login.html', form=form)

# Patient - Registration route
@app.route("/patient/registrierung", methods =["GET", "POST"])
def patient_registration():
    form = PatientRegistrationForm()
    
    # If the form is submitted and validated then...
    if form.validate_on_submit():
        
        # a new patient is added to the database
        new_patient = Patient(f_name=form.f_name.data, l_name=form.l_name.data, date_of_birth=form.date_of_birth.data, unique_patient_identifier=form.unique_patient_identifier.data, password=form.password.data)
        db.session.add(new_patient)
        db.session.commit()
        
        return redirect(url_for('patient_login'))
    
    return render_template('patient/patient_registration.html', form=form)

@app.route("/patient/impfeintrag")
@login_required
def patient_vaccination_entry():
    return render_template('patient/patient_vaccination_entry.html')

@app.route("/patient/impfeintrag/manuell", methods=['POST', 'GET'])
@login_required
def addVaccination():

    form = AddVaccination()
    
    form.vaccination_id.choices = [(int(vaccination.vaccination_id), vaccination.disease + " (" + vaccination.vaccine_category + ")") for vaccination in Vaccination.query.all()]
    
    if form.is_submitted():
        unique_certificate_identifier = 1
        while Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first() is not None:
            unique_certificate_identifier = unique_certificate_identifier + 1

        #unique_patient_identifier ?
        # print(form.vaccine_category.data)
        #date_of_vaccinaion = datetime.date(form.date_of_vaccination.data)
        new_vaccination = Proof_of_vaccination(unique_certificate_identifier=unique_certificate_identifier, unique_patient_identifier= current_user.unique_patient_identifier, date_of_vaccination = form.date_of_vaccination.data, vaccine = form.vaccine.data, batch_number=form.batch_number.data, vaccination_id=form.vaccination_id.data, unique_issuer_identifier=form.unique_issuer_identifier.data, vaccine_marketing_authorization_holder= "/", issued_at= "1900-01-01 00:00:00")
        db.session.add(new_vaccination)
        db.session.commit()
        
        #flash('Impfeintrag erstellt!')
        return redirect(url_for('patient_home'))

    return render_template('patient/patient_vaccination_manual_entry.html', form=form)

@app.route("/patient/impfwissen")
@login_required
def patient_impfwissen():
    return render_template("/patient/patient_vaccination_knowledge.html")

@app.route("/patient/kalender")
@login_required
def patient_kalender():
    return render_template("/patient/patient_calendar.html")

@app.route("/patient/impfeintrag/scan",methods =["GET", "POST"])
@login_required
def patient_scan():
    form = ScanQRForm()
    new_entry = {}
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
            new_entry = Proof_of_vaccination(unique_certificate_identifier = '3', f_name =certificate_data['f_name'], date_of_vaccination = certificate_data['date_of_vaccination'], vaccine = certificate_data['vaccine'], batch_number=certificate_data['batch_number'], vaccine_category=certificate_data['vaccine_category'], unique_issuer_identifier=certificate_data['certificate_issuer'], disease= certificate_data['disease'], vaccine_marketing_authorization_holder= certificate_data['vaccine_marketing_authorization_holder'], issued_at= certificate_data['issued_at'])
            print (certificate_data['f_name'])
        cv2.imshow('Impfnachweis einlesen',frame) # show the frame
        key = cv2.waitKey(1)
        if key ==27:
            break
        db.session.add(new_entry)
        db.session.commit()
        return render_template("/patient/patient_vaccination_certificate.html",form=form)

        #add_certificate_data = Proof_of_vaccination(f_name =form.f_name.data, date_of_vaccination = form.date_of_vaccination.data, vaccine = form.vaccine.data, batch_number=form.batch_number.data, vaccine_category=form.vaccine_category.data, unique_issuer_identifier=form.unique_issuer_identifier.data, disease= "/", vaccine_marketing_authorization_holder= "/", issued_at= "/")
        #db.session.add(nadd_certificate_data)
        #db.session.commit()
    return render_template("/patient/patient_scan.html",form=form)

@app.route("/patient/profil", methods =["GET", "POST"])
@login_required
def patient_profil():
    
    form = PatientUpdateForm()
    
    # Saving the new entered data in the database
    if form.validate_on_submit():
        current_user.f_name = form.f_name.data
        current_user.l_name = form.l_name.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.password = form.password.data
        db.session.commit()

        return redirect(url_for('patient_profil'))
    
    # Reading out the current data and filling it in the forms
    elif request.method == 'GET':
        form.f_name.data = current_user.f_name
        form.l_name.data = current_user.l_name
        form.date_of_birth.data = current_user.date_of_birth
        form.password.data = current_user.password

    return render_template("/patient/patient_profile.html", form=form)



# 
# Issuer routes
#



# Issuer - Login route
@app.route("/issuer/login", methods =["GET", "POST"])
def issuer_login():
    
    # Redirects user to the issuer landing page, if he is already signed in
    if current_user.is_authenticated:
        if session['user_type'] == 'issuer':
            return redirect(url_for('issuer_create_qr'))
    
    # Loads the IssuerLoginForm from forms.py 
    form = IssuerLoginForm()
    
    # If the form is submitted and validated then...
    if form.validate_on_submit():
        
        # Database is queryed based on the unique_issuer_identifier
        issuer = Issuer.query.filter_by(unique_issuer_identifier=form.unique_issuer_identifier.data).first()
        
        # If a issuer with the entered unique_issuer_identifier exists and the password in the database is the same as in the form then...
        if issuer and issuer.password == form.password.data:
            
            # Issuer is written into a cookie and user is logged in
            session['user_type'] = 'issuer'
            login_user(issuer, remember=form.remember.data)
            
            # Issuer is redirected to the issuer landing page
            return redirect(url_for('issuer_create_qr'))

        else:
            flash('Es existiert kein Issuer mit dieser Nutzer ID!', 'danger')
            return redirect(url_for('issuer_login'))
    
    return render_template('issuer/issuer_login.html', form=form)

# Issuer - Registration route
@app.route("/issuer/registrierung", methods =["GET", "POST"])
def issuer_registration():
    form = IssuerRegistrationForm()
    
    if form.validate_on_submit():
        new_issuer = Issuer(f_name=form.f_name.data, l_name=form.l_name.data, date_of_birth=form.date_of_birth.data, unique_issuer_identifier=form.unique_patient_identifier.data, password=form.password.data)
        db.session.add(new_issuer)
        db.session.commit()
        
        return redirect(url_for('issuer_login'))
    
    return render_template('issuer/issuer_registration.html', form=form)


# Landing page route
@app.route("/issuer", methods =["GET", "POST"])
@login_required
def issuer_create_qr():
    form = ImpfnachweisForm()
    form.vaccination_id.choices = [(int(vaccination.vaccination_id), vaccination.disease + " (" + vaccination.vaccine_category + ")") for vaccination in Vaccination.query.all()]
    qr = {}
    img = []
    file_object = io.BytesIO()
## Clicking on the submit button is creating with input data
    if form.is_submitted():
        unique_certificate_identifier = 1
        while Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first() is not None:
            unique_certificate_identifier = unique_certificate_identifier + 1
    
        proof_of_vaccination= {}
        proof_of_vaccination['f_name']= form.f_name.data
        proof_of_vaccination['l_name'] = form.l_name.data
        proof_of_vaccination['date_of_birth']=form.date_of_birth.data
        proof_of_vaccination['date_of_vaccination'] = form.date_of_vaccination.data
        proof_of_vaccination['vaccination_id'] = form.vaccination_id.data
        proof_of_vaccination['vaccine'] = form.vaccine.data
        proof_of_vaccination['vaccine_marketing_authorization_holder'] = form.vaccine_marketing_authorization_holder.data
        proof_of_vaccination['batch_number'] = form.batch_number.data
        proof_of_vaccination['issued_at'] = form.issued_at.data
        proof_of_vaccination['unique_issuer_identifier'] = current_user.unique_issuer_identifier
        proof_of_vaccination['unique_certificate_identifier'] = unique_certificate_identifier
        qr = QRCode(version=1, box_size=3,border=3)
        qr.add_data(proof_of_vaccination)
        qr.make()
        #qr = qrcode.make(proof_of_vaccination)
        img = qr.make_image (fill = 'black', back_color = 'white')
        img.save(file_object,'PNG')
    
    return render_template("/issuer/issuer_create_qr.html", form=form, qr="data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii'))


@app.route("/issuer/impfwissen")
@login_required
def issuer_impfwissen():
    return render_template("issuer/issuer_vaccination_knowledge.html")

@app.route("/issuer/profil", methods =["GET", "POST"])
@login_required
def issuer_profil():
    form = IssuerUpdateForm()
    
    # Saving the new entered data in the database
    if form.validate_on_submit():
        current_user.f_name = form.f_name.data
        current_user.l_name = form.l_name.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.password = form.password.data
        db.session.commit()

        return redirect(url_for('issuer_profil'))
    
    # Reading out the current data and filling it in the forms
    elif request.method == 'GET':
        form.f_name.data = current_user.f_name
        form.l_name.data = current_user.l_name
        form.date_of_birth.data = current_user.date_of_birth
        form.password.data = current_user.password

    return render_template("/issuer/issuer_profile.html", form=form)

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
