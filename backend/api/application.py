"""
application.py
- creates a Flask app instance and registers the database object
"""

from flask import Flask
from flask_cors import CORS

def create_app(app_name='SURVEY_API'):
  app = Flask(app_name)
  app.config.from_object('api.config.BaseConfig')

  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  from api.api import api
  app.register_blueprint(api, url_prefix="/api")

  from api.models import db
  db.init_app(app)

  return app
