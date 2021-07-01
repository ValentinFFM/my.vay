from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField

class ImpfnachweisForm (Form):
    f_name = TextField("Vorname des Geimpften: ")
    l_name = TextField("Nachname des Geimpften: ")
    date_of_birth = DateField("Geburtsdatum des Geimpften: ")
    # issuer_claim?
    date_of_vaccination= DateField("Datum der Impfung: ")
    disease = StringField("Impfung für folgende Krankheit: ")
    vaccine = StringField("Impfstoff: ")
    #medicinal_product = StringField("Name des Impfstoffes: ") # was war medicinal_product?
    vaccine_marketing_authorization_holder = TextField("Hersteller: ")
    batch_number = StringField("Chargennummer: ")
    number_of_doses_expected = IntegerField("Nötige Impfdosen: ")     
    number_of_doses_administered = IntegerField("Bisher erhaltene Impfdosen: ")
    issued_at = DateTimeField ("Ausgestellt am: ")
    member_state = TextField("Land der Ausstellung: ")
    certificate_issuer = StringField("Ihre Zertifikatsnummer: ")
    #generate_unique_certificate_id = StringField("Zertifikatsnummer") --> 
    generate_certificate =  SubmitField("Impfnachweis erstellen")