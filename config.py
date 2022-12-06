from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os.path


# class Config(object):
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'pay-day-time'


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "database2.db")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database2.db')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'pay-day-time'


app = Flask(__name__)
app.config.from_object(Config())
mod = Blueprint('app', __name__)
db = SQLAlchemy(app=app, session_options={'autoflush': False})
csrf = CSRFProtect(app)
