from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField, PasswordField, SelectField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import EqualTo, DataRequired, Length, ValidationError, Email
from my_vay.models import Patient, Issuer

class ImpfnachweisForm (Form):
    f_name = TextField("Vorname des Geimpften: ")
    l_name = TextField("Nachname des Geimpften: ")
    date_of_birth = DateField("Geburtsdatum des Geimpften: ",format='%Y-%m-%d')
    date_of_vaccination= DateTimeField("Datum der Impfung: ",format='%m/%d/%y')
    vaccine_category = TextField("Impfkategorie (Standardimpfung, Auffrischimpfung,...): ")
    disease = StringField("Impfung für folgende Krankheit: ")
    vaccine = StringField("Impfstoff: ")
    vaccine_marketing_authorization_holder = TextField("Hersteller: ")
    batch_number = StringField("Chargennummer: ")
    issued_at = DateTimeLocalField ("Ausgestellt am: ", format='%m/%d/%y')
    certificate_issuer = StringField("Ihre Zertifikatsnummer: ")
    generate_certificate =  SubmitField("Impfnachweis erstellen")

class PatientLoginForm(Form):
    unique_patient_identifier = IntegerField("Nutzer ID", validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Angemeldet bleiben?')
    submit = SubmitField('Login')

class PatientRegistrationForm(Form):
    f_name = StringField('Vorname', validators=[DataRequired()])
    l_name = StringField('Nachname', validators=[DataRequired()])
    date_of_birth = DateField("Geburtsdatum ",validators = [DataRequired()],format='%Y-%m-%d')
    unique_patient_identifier = IntegerField("Nutzer ID")
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Passwort bestätigen', validators=[DataRequired(), EqualTo('password'), Length(min=8)])
    submit = SubmitField('Registrieren')

    #validate unique_patient_identifier and check if it's already existing in patient database
    def validate_unique_patient_identifier(self, unique_patient_identifier):
        unique_patient_identifier = Patient.query.filter_by(unique_patient_identifier=unique_patient_identifier.data).first()

        if unique_patient_identifier:
            raise ValidationError('Diese Nutzer ID ist bereits vergeben.')
        
class PatientUpdateForm(Form):
    f_name = StringField('Vorname', validators=[DataRequired()])
    l_name = StringField('Nachname', validators=[DataRequired()])
    date_of_birth = DateField("Geburtsdatum ",validators = [DataRequired()],format='%Y-%m-%d')
    unique_issuer_identifier = IntegerField("Nutzer ID")
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Speichern')
    
class IssuerLoginForm(Form):
    unique_issuer_identifier = IntegerField("Nutzer ID", validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Angemeldet bleiben?')
    submit = SubmitField('Login')

class IssuerRegistrationForm(Form):
    f_name = StringField('Vorname', validators=[DataRequired()])
    l_name = StringField('Nachname', validators=[DataRequired()])
    date_of_birth = DateField("Geburtsdatum ",validators = [DataRequired()],format='%Y-%m-%d')
    unique_issuer_identifier = IntegerField("Nutzer ID")
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Passwort bestätigen', validators=[DataRequired(), EqualTo('password'), Length(min=8)])
    submit = SubmitField('Registrieren')
    
    #validate unique_patient_identifier and check if it's already existing in patient database
    def validate_unique_issuer_identifier(self, unique_issuer_identifier):
        unique_issuer_identifier = Patient.query.filter_by(unique_issuer_identifier=unique_issuer_identifier.data).first()

        if unique_issuer_identifier:
            raise ValidationError('Diese Nutzer ID ist bereits vergeben.')

class IssuerUpdateForm(Form):
    f_name = StringField('Vorname', validators=[DataRequired()])
    l_name = StringField('Nachname', validators=[DataRequired()])
    date_of_birth = DateField("Geburtsdatum ",validators = [DataRequired()],format='%Y-%m-%d')
    unique_issuer_identifier = IntegerField("Nutzer ID")
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Speichern')
        
class AddVaccination(Form):

    # Creation of all inputfields and the submit button
    date_of_vaccination = DateField('Datum (*)', validators=[DataRequired(), Length(max=30)], render_kw={"placeholder": "YYYY-mm-dd"})
    vaccine = StringField('Impfstoff (*)')
    batch_number = StringField('Chargennummer(*)')
    vaccine_category = SelectField(u'Impfkategorie(*)', choices=[('Gelbfieber', 'Gelbfieber'),('Grippe', 'Grippe'),('Standard','Standard'),('Zusatz','Zusatz')])
    unique_issuer_identifier = SelectField('Issuer ID', choices=[(1,'Impfzentrum A'),(2,'Impfzentrum B')])
    submit = SubmitField('Speichern')

class AddSideeffects(Form):

    # Creation of all inputfields and the submit button
    headache = SelectField(u'Kopfschmerzen', choices=[('Nein', 'Nein'),('Ja', 'Ja')])
    arm_hurts = SelectField(u'Schmerzen an der Einstichstelle', choices=[('Nein', 'Nein'),('Ja', 'Ja')])
    fever = SelectField(u'Fieber', choices=[('Nein', 'Nein'),('Ja', 'Ja')])
    rash = SelectField(u'Ausschlag', choices=[('Nein', 'Nein'),('Ja', 'Ja')])
    tummyache = SelectField(u'Bauchschmerzen oder Übelkeit', choices=[('Nein', 'Nein'),('Ja', 'Ja')])
    sideeffects = StringField('Weitere Nebenwirkungen:')
    submit = SubmitField('Senden')
    
class ScanQRForm(Form):
    scan_qr_code = SubmitField('QR-Code einscannen')
    username = TextField("Nutzername")
    password = PasswordField('Passwort')
    remember = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Login')

class SearchVaccine(Form):

    # Creation of all inputfields and the submit button
    name = StringField('Impfname:')
    submit = SubmitField('Suchen!')


    



