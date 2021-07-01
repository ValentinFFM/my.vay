# Imports from Flask
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy

# Initialize flask application
app = Flask(__name__)

# Location of the database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Master123@localhost:5432/vaccination_database'
app.config['SQLALCHEMY_ECHO'] = True

# Initializing database with SQLAlchemy
db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("landing.html")

# Patient routes
@app.route("/patient")
def patient_home():
    return render_template("/patient/patient_vaccination_certificate.html")

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


# Run application with debug console
if __name__ == "__main__":
    """ """
    app.run(debug=True, host="0.0.0.0", port=3000)