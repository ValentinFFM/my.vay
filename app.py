# Imports from Flask
from flask import Flask, render_template, abort, url_for, redirect
from forms import ImpfnachweisForm

# Initialize flask application
app = Flask(__name__)
# Bootstrap(app)
app.config['SECRET_KEY'] = 'test'

@app.route("/")
def home():
    return render_template("home.html")

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

