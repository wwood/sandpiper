"""
    config.py
    - settings for the flask application object
"""

class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///5_s3_runs.sandpiper.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
