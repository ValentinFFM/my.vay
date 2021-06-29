# Imports from Flask
from flask import Flask, render_template, abort

# Initialize flask application
app = Flask(__name__)

# class Impfung(db.Model):
#     Impfdatum = db.Column(db.String(100))
#     Impfstoff = db.Column(db.String(100))
#     Chargennummer = db.Column(db.String(100), primary_key=True)
#     Impfkategorie = db.Column(db.String(100))
#     Medizinische_Einrichtung = db.Column(db.String(100))

#     def __init__(self, Impfdatum, Impfstoff, Chargennummer, Impfkategorie, Medizinische_Einrichtung):
#         self.Impfdatum = Impfdatum
#         self.Impfstoff = Impfstoff
#         self.Chargennummer = Chargennummer
#         self.Impfkategorie = Impfkategorie
#         self.Medizinische_Einrichtung = Medizinische_Einrichtung
    
#     def __repr__(self):
#         return '<Impfung:%r>' % self.Impfdatum % self.Impfstoff % self.Chargennummer % self.Impfkategorie %self.Medizinische_Einrichtung



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

# Run application with debug console
if __name__ == "__main__":
    """ """
    app.run(debug=True, host="0.0.0.0", port=3000)