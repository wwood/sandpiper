"""
    config.py
    - settings for the flask application object
"""
import os

class BaseConfig:
    DEBUG = True

    LYRA_DB_PATH = 'sqlite:///db/sandpiper_14.sqlite3'

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'running_on_lyra')):
        SQLALCHEMY_DATABASE_URI = LYRA_DB_PATH
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sandpiper_15_test.sqlite3'

    else:        
        ## For deployment
        SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sandpiper_14.sqlite3'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True
