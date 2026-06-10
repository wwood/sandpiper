"""
application.py
- creates a Flask app instance and registers the database object
"""

import json
import traceback
import urllib.request

from flask import Flask, got_request_exception, has_request_context, request
from flask_cors import CORS

import sys
import os

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')] + sys.path

# Discord rejects messages longer than 2000 characters.
_DISCORD_MAX_CONTENT = 2000


def _notify_admin(exception):
    # Errors are reported to a Discord channel via an incoming webhook. It is a
    # no-op unless SANDPIPER_DISCORD_WEBHOOK_URL is set (e.g. in production), so
    # local/dev runs are unaffected. The webhook URL is a secret: anyone holding
    # it can post to the channel, so inject it at runtime, never commit it.
    webhook_url = os.environ.get('SANDPIPER_DISCORD_WEBHOOK_URL')
    if not webhook_url:
        return

    # The full traceback plus the request that triggered it.
    tb = ''.join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )
    header = 'Sandpiper error: {}'.format(type(exception).__name__)
    if has_request_context():
        header += '\n{} {}'.format(request.method, request.url)

    # Keep the tail of the traceback (the actual error) if we'd exceed the limit.
    message = '{}\n```\n{}\n```'.format(header, tb)
    if len(message) > _DISCORD_MAX_CONTENT:
        budget = _DISCORD_MAX_CONTENT - len(header) - len('\n```\n…\n\n```')
        message = '{}\n```\n…\n{}\n```'.format(header, tb[-budget:])

    data = json.dumps({'content': message}).encode('utf-8')
    req = urllib.request.Request(
        webhook_url, data=data, headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        # Never let error reporting break request handling.
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
