from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config.from_object('config')
db = SQLAlchemy(app)

from .models import *
from .views import *
