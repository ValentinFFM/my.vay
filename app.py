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

#Location of the database 
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

class AddVaccination(Form):

    # Creation of all inputfields and the submit button
    date_of_vaccination = DateField('Datum (*)', validators=[DataRequired(), Length(max=30)])
    vaccine = StringField('Impfstoff (*)', validators=[DataRequired(), Length(max=30)])
    batch_number = StringField('Chargennummer(*)',  validators=[DataRequired()])
    vaccine_category = StringField('Impfkategorie(*)', validators=[Length(max=60)])
    unique_issuer_identifier = StringField('Medizinische Einrichtung', validators=[Length(max=30)])
    submit = SubmitField('Speichern')
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

@app.route("/patient/impfeintrag-neu")
def patient_vaccination_entry():
    return render_template('patient/patient_vaccination_entry.html')

@app.route("/vaccination/add", methods=['POST', 'GET'])
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

