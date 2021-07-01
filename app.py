# Imports from Flask
from flask import Flask, render_template, abort, url_for, redirect
from forms import ImpfnachweisForm

# Initialize flask application
app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = 'test'

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


@app.route("/issuer/QR", methods =["GET", "POST"])   
def issuer_create_qr():
    #fields = NONE
    form = ImpfnachweisForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template("/issuer/issuer_create_qr.html", form=form)

# Run application with debug console
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

