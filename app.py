# Imports from Flask
from flask import Flask, render_template, abort
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Lenght, AnyOf
from flask_bootstrap import Bootstrap
# Initialize flask application
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'DontTellAnyone'

class LoginForm(Form):
    username = StringField('username', validators=[InputRequired(), Email(message='Wrong Email.')])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=10), AnyOf(['secret','password'])])

@app.route("/", methods=['GET', 'POST'])
def issuer_login():
    form = LoginForm()
    if form.validate_on_submit():
        return 'Form Successfully Submitted!'
    return render_template('issuer_login.html', form=form)

# Run application with debug console
if __name__ == "__main__":
    """ """
    app.run(debug=True)


