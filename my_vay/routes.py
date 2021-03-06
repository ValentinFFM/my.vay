# 
# Imports
#

from my_vay import app, db

# General imports for Flask
from flask import render_template, abort, url_for, redirect, flash, request, session, Response

# Imports for forms
from my_vay.forms import AddSideeffects, ImpfnachweisForm, PatientLoginForm, AddVaccination, PatientRegistrationForm, IssuerRegistrationForm, IssuerLoginForm, IssuerUpdateForm, PatientUpdateForm, SearchVaccine

# Imports for user handeling
from flask_login import login_user, current_user, logout_user, login_required

# Imports for models
from my_vay.models import Patient, Issuer, Proof_of_vaccination, Vaccination, Sideeffects

# Imports for QR-Code creation and encoding
from base64 import b64encode, decode
import io
from qrcode.main import QRCode
import cv2
import ast
import sys
from pyzbar import pyzbar
from pyzbar.pyzbar import decode

# Imports for datetime
from datetime import date, timedelta
from dateutil import relativedelta

#
# Base functions
#

# Decoding a QR-Code in a given frame
def decode_QR_code_from_frame(frame):
    # Decode QR-Code
    decodedObject = pyzbar.decode(frame)

    # If decodedObject exists, then the data is returned as string
    if decodedObject:
        # Read out the data of the QR-Code
        decodedObjectData = decodedObject[0].data
        
        # Decode the content with UTF-8
        decodedObjectDataUTF = decodedObjectData.decode('utf-8')
        
        # Covert String to 
        decodedObjectDict = ast.literal_eval(decodedObjectDataUTF)
        
        return decodedObjectDict

# Calling decode_QR_code_from_frame(frame) for every frame of the camera
def read_in_frame_for_decoding():
    # Instanciation of a camera object
    camera = cv2.VideoCapture(0)
    
    # For every frame of the camera the function decode_QR_code_from_frame() is called, until the decode_QR_code_from_frame() function returns a result
    while True:
        success, frame = camera.read()

        if not success:
            break
        else:
            decodedObject = decode_QR_code_from_frame(frame)

            if decodedObject:
                break
    
    return decodedObject

# Function for returning notifications for missing vaccinations
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

# Function to deside whether a sideeffect reminder should be shown or not, is called in patient_home
def show_sideeffect():
    from datetime import date
    today = 0
    sideeffects_list=[]
    sf_show = Proof_of_vaccination.query.filter_by(unique_patient_identifier=current_user.unique_patient_identifier).all()
    sideeffect_check = Sideeffects.query.all()
    today = date.today()
    #get the date of yesterday
    for i in range (1):
            today-= timedelta(days=1)
    today = today.strftime('%Y-%m-%d')

    #checks if a vaccination has the same date as the today variable, because then a reminder should be shown
    for entry in sf_show:
        classifier= False
        if entry.date_of_vaccination.strftime('%Y-%m-%d') == today:
            for val in sideeffect_check:
                    if entry.unique_certificate_identifier == val.unique_certificate_identifier:
                        classifier = True
                        break
            if classifier == False:
                #sideeffects can only be entered if an entry for this vaccination does not already exist
                sideeffects_list.append(entry)
    # reuturns list of vaccination entries in proof_of_vaccination that fulfill conditions
    return sideeffects_list

#
# General routes
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

#  Camera stream route 
@app.route("/camera_stream")
def camera_stream():
    
    def generate_frames():
        # Instantiation of a camera object refering to the camera of the device
        camera = cv2.VideoCapture(0)
        
        while True:
            # Getting frames from the camera
            success, frame = camera.read()

            if not success:
                break
            else:
                # Coverting frames to a jpg
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

    # Returning frames of the facecame
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#
# Patient routes
#

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

# Patient - Landing page route
@app.route("/patient",methods=['POST', 'GET'])
@app.route("/patient/<string:sort>", methods=['POST', 'GET'])
@app.route("/patient/<string:sort>/<string:search>", methods=['POST', 'GET'])
@login_required
def patient_home(sort='date', search=''):
    
    page = request.args.get('page', 1, type=int)
    #shows search form
    form = SearchVaccine()
    vaccine_search = False

    # Checks if a search term is used. If yes then only vaccinations are shown that fulfill the vaccine search statement. Otherwise all vaccinations entries for this patient are shown.
    if search:
        vaccine_search = True
        search = '%' + search + '%'
        branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).filter(Proof_of_vaccination.vaccine.like(search)).paginate(page=page, per_page=5)
        vaccination = Vaccination.query.filter(Proof_of_vaccination.vaccination_id == Vaccination.vaccination_id).all()
    else: 
        # Depending on an argument in the url, the patients are sorted in different ways. The value 'date' is set as the default sort value. All vaccination entries are shown in ordered by date_of_vaccination.
        if sort == 'date':
            branch = Proof_of_vaccination.query.filter_by(unique_patient_identifier=current_user.unique_patient_identifier).order_by(Proof_of_vaccination.date_of_vaccination.desc()).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Proof_of_vaccination.vaccination_id == Vaccination.vaccination_id).all()

        # Different filter values can be selected through the drop-down-menu   
        elif sort == 'Pneumokokken':
            branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Vaccination.disease == sort).all()

        elif sort == 'Hepatitis B':
            branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Vaccination.disease == sort).all()

        elif sort == 'COVID-19':
            branch = Proof_of_vaccination.query.filter(Proof_of_vaccination.unique_patient_identifier == current_user.unique_patient_identifier).paginate(page=page, per_page=5)
            vaccination = Vaccination.query.filter(Vaccination.disease == sort).all()   
          
        else:
            abort(404)

    # runs if a search value was submitted
    if form.is_submitted():
        return redirect(url_for('patient_home', sort='date', search=form.name.data))
    
    #call the functions check_for_vac_notifications() and show_sideeffect()
    vac_notifications = check_for_vac_notifications()
    vac_sideeffects = show_sideeffect()

    return render_template('patient/patient_vaccination_certificate.html', branch=branch, sort=sort, form=form, search=vaccine_search, vac_notifications=vac_notifications, vac_sideeffects=vac_sideeffects, vaccination=vaccination)

# Patient - Show QR-Code of proof_of_vaccination
@app.route("/patientQR/<int:unique_certificate_identifier>", methods=['POST', 'GET'])
def open_QR(unique_certificate_identifier):

    # collects the values for the selected vaccination entry so a QR code can be generated
    branch = Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first()
    vaccination = Vaccination.query.filter(Proof_of_vaccination.vaccination_id == Vaccination.vaccination_id).first()

    qr = {}
    img = []
    file_object = io.BytesIO()

    # save vaccinations values in dictionary
    proof_of_vaccination= {}
    proof_of_vaccination['unique_certificate_identifier']= branch.unique_certificate_identifier
    proof_of_vaccination['date_of_vaccination']= branch.date_of_vaccination.strftime('%Y-%m-%d')
    proof_of_vaccination['vaccine']= branch.vaccine
    proof_of_vaccination['vaccination_id'] = branch.vaccination_id
    proof_of_vaccination['vaccine_marketing_authorization_holder']= branch.vaccine_marketing_authorization_holder
    proof_of_vaccination['batch_number']= branch.batch_number
    proof_of_vaccination['issued_at']= branch.issued_at.strftime('%Y-%m-%d %H:%M:%S')
    proof_of_vaccination['unique_patient_identifier']= branch.unique_patient_identifier
    proof_of_vaccination['unique_issuer_identifier']= branch.unique_issuer_identifier

    print(proof_of_vaccination)

    # create QR code with given values
    qr = QRCode(version=1, box_size=6,border=4)
    qr.add_data(proof_of_vaccination)
    qr.make()
        #qr = qrcode.make(proof_of_vaccination)
    img = qr.make_image (fill = 'black', back_color = 'white')
    img.save(file_object,'PNG')

    return render_template('patient/patient_show_QR.html', branch = branch, vaccination=vaccination, qr="data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii'))

# Patient - Sideeffects route
# is only callable if show_sideeffect() function is satisfied
@app.route("/patient/sideeffects/<int:unique_certificate_identifier>", methods=['POST', 'GET'])
@login_required
def new_sideeffect(unique_certificate_identifier):
    branch = Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first()

    #shows the form to create a new sideeffect entry
    form = AddSideeffects()
    
    # If the form is submitted then...
    if form.is_submitted():
        unique_entry_identifier = 1
        while Sideeffects.query.filter_by(unique_entry_identifier=unique_entry_identifier).first() is not None:
            unique_entry_identifier = unique_entry_identifier + 1
        # a new sideeffect is added to the database
        new_sideeffects = Sideeffects(unique_entry_identifier=unique_entry_identifier, unique_certificate_identifier=unique_certificate_identifier ,headache=form.headache.data, arm_hurts=form.arm_hurts.data, rash=form.rash.data, fever=form.fever.data, tummyache=form.tummyache.data, sideeffects=form.sideeffects.data)
        db.session.add(new_sideeffects)
        db.session.commit()
        
        return redirect(url_for('patient_home'))
    
    return render_template('patient/patient_sideeffects.html', branch = branch, form=form )

# Patient - Proof of vaccination entry route
@app.route("/patient/impfeintrag")
@login_required
def patient_vaccination_entry():
    #redirects to new html page where a patient can choose between a manual and a scannable entry
    return render_template('patient/patient_vaccination_entry.html')

# Patient - Proof of vaccination manual entry route 
@app.route("/patient/impfeintrag/manuell", methods=['POST', 'GET'])
@login_required
def addVaccination():

    # shows form to create a new vaccination entry - this entry is not verified so no QR code can be displayed for it later
    form = AddVaccination()
    
    # selects drop-down-choices for the vaccination_id SelectField (vaccine_category and disease are shown in frontend instead of vaccination_id)
    form.vaccination_id.choices = [(int(vaccination.vaccination_id), vaccination.disease + " (" + vaccination.vaccine_category + ")") for vaccination in Vaccination.query.all()]
    
    # if the form is submitted...
    if form.is_submitted():
        # the next open unique_certificate_identifier is selected...
        unique_certificate_identifier = 1
        while Proof_of_vaccination.query.filter_by(unique_certificate_identifier=unique_certificate_identifier).first() is not None:
            unique_certificate_identifier = unique_certificate_identifier + 1
        # and a new vaccination entry is added to the database, issed_at value and vaccine_marketing_authorization_holder get a default value, because the vaccination entry is not verified
        new_vaccination = Proof_of_vaccination(unique_certificate_identifier=unique_certificate_identifier, unique_patient_identifier= current_user.unique_patient_identifier, date_of_vaccination = form.date_of_vaccination.data, vaccine = form.vaccine.data, batch_number=form.batch_number.data, vaccination_id=form.vaccination_id.data, unique_issuer_identifier=form.unique_issuer_identifier.data, vaccine_marketing_authorization_holder= "/", issued_at= "1900-01-01 00:00:00")
        db.session.add(new_vaccination)
        db.session.commit()
        
        #flash('Impfeintrag erstellt!')
        return redirect(url_for('patient_home'))

    return render_template('patient/patient_vaccination_manual_entry.html', form=form)

# Patient - Proof of vaccination QR-Code entry route
@app.route("/patient/impfeintrag/scan",methods =["GET", "POST"])
@login_required
def patient_scan():
    return render_template("/patient/patient_scan.html")

# Patient - QR-Code result route
@app.route("/patient/impfeintrag/scan-result")
@login_required
def patient_qr_result():
    
    # Calls read_in_frame_for_decoding(), which returns a dictionary representing the proof of vaccination
    proof_of_vaccination_qr = read_in_frame_for_decoding()
    
    # Checks if proof_of_vaccination is already existing in the database. If so, then an error message is displayed.
    if Proof_of_vaccination.query.filter_by(unique_certificate_identifier = proof_of_vaccination_qr["unique_certificate_identifier"]).first():
        error_message = """Beim Scannen des QR-Codes ist ein Fehler aufgetreten. Dieser QR-Code wurde bereits von Ihrem oder einem anderen Konto
                        eingescannt."""
        return render_template("patient/patient_scan_result.html", error_message=error_message)
    
    else:
        # Checks if the issuer of the certificate is existing in the database
        if Issuer.query.filter_by(unique_issuer_identifier = proof_of_vaccination_qr["unique_issuer_identifier"]).first():
            
            # Checks if first name, last name and birthdate are the same of proof_of_vaccination and the logged in user.
            if proof_of_vaccination_qr['f_name'] == current_user.f_name and proof_of_vaccination_qr['l_name'] == current_user.l_name and proof_of_vaccination_qr['date_of_birth'] == str(current_user.date_of_birth):
                # If it's the same, then the proof_of_vaccination is added to the database.
                new_vaccination = Proof_of_vaccination(unique_certificate_identifier = proof_of_vaccination_qr["unique_certificate_identifier"], 
                                                    unique_patient_identifier = current_user.unique_patient_identifier, 
                                                    date_of_vaccination = proof_of_vaccination_qr["date_of_vaccination"], 
                                                    vaccine = proof_of_vaccination_qr["vaccine"], 
                                                    batch_number = proof_of_vaccination_qr["batch_number"], 
                                                    vaccination_id = proof_of_vaccination_qr["vaccination_id"], 
                                                    unique_issuer_identifier = proof_of_vaccination_qr["unique_issuer_identifier"], 
                                                    vaccine_marketing_authorization_holder= proof_of_vaccination_qr["vaccine_marketing_authorization_holder"], 
                                                    issued_at = proof_of_vaccination_qr["issued_at"])
                db.session.add(new_vaccination)
                db.session.commit()

                return render_template("patient/patient_scan_result.html", proof_of_vaccination_qr=proof_of_vaccination_qr)
            else:
                # If the data is not equal, then an error message is displayed.
                error_message = """Beim Scannen des QR-Codes ist ein Fehler aufgetreten. Sie haben versucht den QR-Code eines Impfnachweises
                                zu Scannen, welcher nicht f??r Sie ausgestellt wurde. Bitte ??berpr??fen Sie, mit welchem Konto Sie angemeldet
                                sind und ob Ihr Impfnachweis die korrekten Daten enth??lt."""
                return render_template("patient/patient_scan_result.html", error_message=error_message)
        else:
            # If the issuer is not existing, then an error message is displayed.
            error_message = """Beim Scannen des QR-Codes ist ein Fehler aufgetreten. Sie haben versucht den QR-Code eines Impfnachweises
                            zu Scannen, welcher nicht von einem verifizierten Issuer ausgestellt wurde."""
            return render_template("patient/patient_scan_result.html", error_message=error_message)

# Patient - Vaccination knowledge route
@app.route("/patient/impfwissen")
@login_required
def patient_impfwissen():
    return render_template("/patient/patient_vaccination_knowledge.html")

# Patient - Calendar route
@app.route("/patient/kalender")
@login_required
def patient_kalender():
    return render_template("/patient/patient_calendar.html")

# Patient - Profile route
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
    if form.is_submitted():
        
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
        new_issuer = Issuer(f_name=form.f_name.data, l_name=form.l_name.data, date_of_birth=form.date_of_birth.data, unique_issuer_identifier=form.unique_issuer_identifier.data, password=form.password.data)
        db.session.add(new_issuer)
        db.session.commit()
        
        return redirect(url_for('issuer_login'))
    
    return render_template('issuer/issuer_registration.html', form=form)

# Issuer - Landing page route
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
        proof_of_vaccination['date_of_birth'] = form.date_of_birth.data.strftime('%Y-%m-%d')
        proof_of_vaccination['date_of_vaccination'] = form.date_of_vaccination.data.strftime('%Y-%m-%d')
        proof_of_vaccination['vaccination_id'] = form.vaccination_id.data
        proof_of_vaccination['vaccine'] = form.vaccine.data
        proof_of_vaccination['vaccine_marketing_authorization_holder'] = form.vaccine_marketing_authorization_holder.data
        proof_of_vaccination['batch_number'] = form.batch_number.data
        proof_of_vaccination['issued_at'] = form.issued_at.data.strftime('%Y-%m-%d %H:%M:%S')
        proof_of_vaccination['unique_issuer_identifier'] = current_user.unique_issuer_identifier
        proof_of_vaccination['unique_certificate_identifier'] = unique_certificate_identifier
        qr = QRCode(version=1, box_size=3,border=3)
        qr.add_data(proof_of_vaccination)
        qr.make()
        #qr = qrcode.make(proof_of_vaccination)
        img = qr.make_image (fill = 'black', back_color = 'white')
        img.save(file_object,'PNG')
    
    return render_template("/issuer/issuer_create_qr.html", form=form, qr="data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii'))

# Issuer - Vaccination knowledge route
@app.route("/issuer/impfwissen")
@login_required
def issuer_impfwissen():
    return render_template("issuer/issuer_vaccination_knowledge.html")

# Issuer - Profile route
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



# 
# Verifier routes
#

# Verifier - QR-Code scan route 
@app.route("/verifier", methods =["GET", "POST"])
def verifier_qr_scan():
    return render_template("verifier/verifier_scan.html")

# Verifier - QR-Code result route
@app.route("/verifier/scan-result")
def verifier_qr_result():
    proof_of_vaccination_correct = False
    patient = None
    
    proof_of_vaccination_qr = read_in_frame_for_decoding()
    
    # Checks if encoded QR-code contains all relevant data
    if "unique_certificate_identifier" in proof_of_vaccination_qr and "date_of_vaccination" in proof_of_vaccination_qr and "vaccine" in proof_of_vaccination_qr and "vaccine_marketing_authorization_holder" in proof_of_vaccination_qr and "batch_number" in proof_of_vaccination_qr and "issued_at" in proof_of_vaccination_qr and "unique_patient_identifier" in proof_of_vaccination_qr and "unique_issuer_identifier" in proof_of_vaccination_qr and "vaccination_id" in proof_of_vaccination_qr:
        
        unique_certificate_identifier = proof_of_vaccination_qr["unique_certificate_identifier"],
        date_of_vaccination = proof_of_vaccination_qr["date_of_vaccination"],
        vaccine = proof_of_vaccination_qr["vaccine"],
        vaccine_marketing_authorization_holder = proof_of_vaccination_qr["vaccine_marketing_authorization_holder"],
        batch_number = proof_of_vaccination_qr["batch_number"],
        issued_at = proof_of_vaccination_qr["issued_at"],
        unique_patient_identifier = proof_of_vaccination_qr["unique_patient_identifier"],
        unique_issuer_identifier = proof_of_vaccination_qr["unique_issuer_identifier"],
        vaccination_id = proof_of_vaccination_qr["vaccination_id"]
        
        # Checks if proof_of_vaccination exists in the database
        if Proof_of_vaccination.query.filter_by(unique_certificate_identifier = unique_certificate_identifier,
                                            date_of_vaccination = date_of_vaccination,
                                            vaccine = vaccine,
                                            vaccine_marketing_authorization_holder = vaccine_marketing_authorization_holder,
                                            batch_number = batch_number,
                                            issued_at = issued_at,
                                            unique_patient_identifier = unique_patient_identifier,
                                            unique_issuer_identifier = unique_issuer_identifier,
                                            vaccination_id = vaccination_id
                                            ).first():
            
            patient = Patient.query.filter_by(unique_patient_identifier=unique_patient_identifier).first()
            proof_of_vaccination_correct = True

    return render_template("verifier/verifier_scan_result.html", proof_of_vaccination_correct=proof_of_vaccination_correct, patient=patient)
