from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = '767656chay'
#account_sid = 'ACd0c312ca8abe224bdee296a629f0b930'
#auth_token = 'c9215cc3a49810beb88c955f326e7179'
#twilio_phone_number = '+12564484851'

#client = Client(account_sid, auth_token)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from application import routes,watchlist, prediction, visual,models
