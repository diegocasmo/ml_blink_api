from dotenv import load_dotenv
load_dotenv() # Load environmental variables

import os
from flask import Flask
from flask_cors import CORS
from ml_blink_api.resources.users.controllers import users
from ml_blink_api.resources.sessions.controllers import sessions
from ml_blink_api.resources.matchings.controllers import matchings

app = Flask(__name__)
app.debug = os.getenv('DEBUG')
app.secret_key = os.getenv('SECRET_KEY')
CORS(app)

app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(sessions, url_prefix='/sessions')
app.register_blueprint(matchings, url_prefix='/matchings')
