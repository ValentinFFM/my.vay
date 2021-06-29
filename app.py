# Imports from Flask
from flask import Flask, render_template, abort
from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, Length
# from flask_bootstrap import Bootstrap

# Initialize flask application
app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = ''


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




@app.route("/")
def home():
    return render_template("home.html")

@app.route("/QR", methods =["GET", "POST"])   
def issuer_create_qr():
    #fields = NONE
    form = ImpfnachweisForm()
    return render_template("issuer_create_qr.html", title = "Impfnachweis erstellen",form=form)

# Run application with debug console
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

