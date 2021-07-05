# Imports from Flask

# Imports from Flask
from flask import Flask, render_template, abort
from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, DataRequired, Email
# from flask_bootstrap import Bootstrap
#from flask_sqlalchemy import SQLAlchemy


# Initialize flask application
app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = 'Test'
#db = SQLAlchemy(app)

class ImpfnachweisForm (Form):
    f_name = TextField("Vorname des Geimpften: ")
    l_name = TextField("Nachname des Geimpften: ")
    date_of_birth = DateField("Geburtsdatum des Geimpften: ")
    # issuer_claim?
    date_of_vaccination= DateField("Datum der Impfung: ")
    disease = StringField("Impfung für folgende Krankheit: ")
    vaccine = StringField("Impfstoff: ")
    medicinal_product = StringField("Name des Impfstoffes: ") # was war medicinal_product?
    vaccine_marketing_authorization_holder = TextField("Hersteller: ")
    batch_number = StringField("Chargennummer: ")
    number_of_doses_expected = IntegerField("Nötige Impfdosen: ")     
    number_of_doses_administered = IntegerField("Bisher erhaltene Impfdosen: ")
    issued_at = DateTimeField ("Ausgestellt am: ")
    member_state = TextField("Land der Ausstellung: ")
    certificate_issuer = StringField("Ihre Zertifikatsnummer: ")
    #generate_unique_certificate_id = StringField("Zertifikatsnummer") --> 
    generate_certificate =  SubmitField("Impfnachweis erstellen")

vaccination =[
    {
        "date_of_vaccination":"01.06.21",
        "vaccine":"BioNTech",
        "batch_number":"128he23bhu",
        "vaccination_category":"Standard",
        "certificate_issuer": "Impfzentrum Frankfurt"

    },
    {
        "date_of_vaccination":"01.09.21",
        "vaccine":"BioNTech",
        "batch_number":"dadsdafaf",
        "vaccination_category":"Standard",
        "certificate_issuer": "Impfzentrum Frankfurt"
    }
]


# class vaccination(db.Model):
    #brauchen wir noch mehr Infos ausgegeben?
    # date_of_vaccination = db.Column(db.String(100))
    # vaccine = db.Column(db.String(100))
    # batch_number = db.Column(db.String(100), primary_key=True)
    # vaccination_category = db.Column(db.String(100))
    # certificate_issuer = db.Column(db.String(100))

    # def __init__(self, date_of_vaccination, vaccine, batch_number, vaccination_category, certificate_issuer):
    #     self.date_of_vaccination = date_of_vaccination
    #     self.vaccine = vaccine
    #     self.batch_number = batch_number
    #     self.vaccination_category = vaccination_category
    #     self.certificate_issuer = certificate_issuer
    
    # def __repr__(self):
    #     return '<Impfung:%r>' % self.date_of_vaccination % self.vaccine % self.batch_number % self.vaccination_category %self.certificate_issuer

class AddVaccination(Form):

    # Creation of all inputfields and the submit button
    date_of_vaccination = DateField('Datum (*)', validators=[DataRequired(), Length(max=30)])
    vaccine = StringField('Impfstoff (*)', validators=[DataRequired(), Length(max=30)])
    batch_number = StringField('Chargennummer(*)',  validators=[DataRequired()])
    vaccination_category = StringField('Impfkategorie(*)', validators=[Length(max=60)])
    certificate_issuer = StringField('Medizinische Einrichtung', validators=[Length(max=30)])
    submit = SubmitField('Speichern')

@app.route("/vaccination/add", methods=['POST', 'GET'])
#@login_required
def addVaccination():

    form = AddVaccination()

    # if form.validate_on_submit():
    # Inserts a patient and a relative to the patient the SQL databs
    # patient = vaccination(date_of_vaccination=form.date_of_vaccination.data, vaccine=form.vaccine.data, batch_number=form.batch_number.data, vaccination_category=form.vaccination_category.data, certificate_issuer=form.certificate_issuer.data)
    # db.session.add(vaccination)
    # db.session.commit()

    # flash('Impfeintrag erstellt!')
    # return redirect(url_for('patient_vaccination_certificate'))

    return render_template('patient/patient_vaccination_manual_entry.html', form=form)

@app.route("/")
def home():
    return render_template("landing.html")

# Impdaten anzeigen

@app.route("/patient")
def patient_home():
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

# Run application with debug console
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

