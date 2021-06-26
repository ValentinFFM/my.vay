# Imports from Flask
from flask import Flask, render_template, abort

# Initialize flask application
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("landing.html")

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

# Run application with debug console
if __name__ == "__main__":
    """ """
    app.run(debug=True, host="0.0.0.0", port=3000)