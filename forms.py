from flask_wtf import Form
from wtforms import TextField, StringField, DateTimeField, BooleanField, SubmitField, IntegerField, DateField, PasswordField, SelectField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import EqualTo, DataRequired, Length, ValidationError, Email
#from models import Patient
from wtforms.validators import EqualTo, ValidationError 

class ImpfnachweisForm (Form):
    f_name = TextField("Vorname des Geimpften: ")
    l_name = TextField("Nachname des Geimpften: ")
    date_of_birth = DateField("Geburtsdatum des Geimpften: ",format='%m/%d/%y')
    date_of_vaccination= DateField("Datum der Impfung: ",format='%m/%d/%y')
    vaccine_category = TextField("Impfkategorie (Standardimpfung, Auffrischimpfung,...): ")
    disease = StringField("Impfung für folgende Krankheit: ")
    vaccine = StringField("Impfstoff: ")
    vaccine_marketing_authorization_holder = TextField("Hersteller: ")
    batch_number = StringField("Chargennummer: ")
    issued_at = DateTimeLocalField ("Ausgestellt am: ", format='%m/%d/%y')
    certificate_issuer = StringField("Ihre Zertifikatsnummer: ")
    generate_certificate =  SubmitField("Impfnachweis erstellen")

class LoginForm(Form):
    username = TextField("Nutzerkennung")
    password = PasswordField('Passwort')
    remember = BooleanField('Passwort vergessen')
    submit = SubmitField('Login')


class RegistrationForm(Form):
    f_name = StringField('Vorname', validators=[DataRequired()])
    l_name = StringField('Nachname', validators=[DataRequired()])
    date_of_birth = DateField("Geburtsdatum des Geimpften: ",validators = [DataRequired()],format='%Y-%m-%d')
    unique_patient_identifier = StringField("Nutzerkennung")
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Passwort bestätigen', validators=[DataRequired(), EqualTo('password'), Length(min=8)])
    submit = SubmitField('Registrieren')

#validate unique_patient_identifier and check if it's already existing in patient database 
    #def validate_unique_patient_identifier(self, unique_patient_identifier):
    
        #unique_patient_identifier = Patient.query.filter_by(unique_patient_identifier=unique_patient_identifier.data).first()
        #if unique_patient_identifier:
            #raise ValidationError('Nutzerkennung bereits vergeben')
        
class AddVaccination(Form):

    # Creation of all inputfields and the submit button
    
    date_of_vaccination = DateField('Datum (*)', validators=[DataRequired(), Length(max=30)], render_kw={"placeholder": "%Y-%m-%d"})
    vaccine = StringField('Impfstoff (*)')
    batch_number = StringField('Chargennummer(*)')
    vaccine_category = SelectField(u'Impfkategorie(*)', choices=[(1,'Standard'),(2, 'Gelbfieber')])
    unique_issuer_identifier = StringField('Issuer ID')
    submit = SubmitField('Speichern')



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