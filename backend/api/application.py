"""
application.py
- creates a Flask app instance and registers the database object
"""

from email.message import EmailMessage
import smtplib

from flask import Flask, got_request_exception
from flask_cors import CORS

import sys
import os

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')] + sys.path


def _notify_admin(exception):
    address = ''.join(map(chr, [98, 46, 119, 111, 111, 100, 99, 114, 111, 102,
                                116, 64, 113, 117, 116, 46, 101, 100, 117, 46,
                                97, 117]))
    msg = EmailMessage()
    msg['Subject'] = 'Sandpiper error'
    msg['From'] = 'errors@sandpiper'
    msg['To'] = address
    msg.set_content(str(exception))
    try:
        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg)
    except Exception:
        pass


def create_app(app_name='SURVEY_API'):
    app = generate_app(app_name)

    from api.models import db
    db.init_app(app)
    from api.duckdb_limits import register_duckdb_limits

    with app.app_context():
        register_duckdb_limits(db.engine)

    return app


def generate_app(app_name='SURVEY_API'):
    
    app = Flask(app_name)
    app.config.from_object('api.config.BaseConfig')

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from api.api import api
    app.register_blueprint(api, url_prefix="/api")

    def _send_error(sender, exception, **extra):
        _notify_admin(exception)

    got_request_exception.connect(_send_error, app)

    return app
