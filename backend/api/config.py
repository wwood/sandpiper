"""
    config.py
    - settings for the flask application object
"""
import os

class BaseConfig:
    DEBUG = True

    LYRA_DB_PATH = 'sqlite:///db/sandpiper_16.sqlite3'
    PROD_DB_PATH = LYRA_DB_PATH

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'running_on_lyra')):
        SQLALCHEMY_DATABASE_URI = LYRA_DB_PATH
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sandpiper_15_test.sqlite3'

    else:        
        ## For deployment
        SQLALCHEMY_DATABASE_URI = PROD_DB_PATH
    print("Connecting to db {}".format(SQLALCHEMY_DATABASE_URI))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True
