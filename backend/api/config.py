"""
    config.py
    - settings for the flask application object
"""

class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///6_runs.sandpiper.sqlite3'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sra_20211215.mach1.sandpiper2.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True
