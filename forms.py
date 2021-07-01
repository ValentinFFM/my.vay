from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField

class ImpfnachweisForm (Form):
    f_name = TextField("Vorname des Geimpften: ")
    l_name = TextField("Nachname des Geimpften: ")
    date_of_birth = DateField("Geburtsdatum des Geimpften: ")
    # issuer_claim?
    date_of_vaccination= DateField("Datum der Impfung: ")
    vaccine_category = TextField("Impfkategorie (Standarfimpfung, Auffrischimpfung,...): ")
    disease = StringField("Impfung für folgende Krankheit: ")
    vaccine = StringField("Impfstoff: ")
    vaccine_marketing_authorization_holder = TextField("Hersteller: ")
    batch_number = StringField("Chargennummer: ")
    issued_at = DateTimeField ("Ausgestellt am: ")
    certificate_issuer = StringField("Ihre Zertifikatsnummer: ")
    generate_certificate =  SubmitField("Impfnachweis erstellen")