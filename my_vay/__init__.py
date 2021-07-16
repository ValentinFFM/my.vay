
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 
# Initialization of Flask Application
#
app = Flask(__name__)

app.config['SECRET_KEY'] = 'test'

#
# Initializing database with SQLAlchemy
#
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/vaccination_database'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# 
# Initialization of the LoginManager, which handels the user sessions in the browser to ensure that users must be logged in for the application.
# 
loginManager = LoginManager(app)
loginManager.login_view = 'patient_login'
loginManager.login_message_category = 'info'

from my_vay import routes