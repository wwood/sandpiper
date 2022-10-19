"""
    config.py
    - settings for the flask application object
"""
import os

class BaseConfig:
    DEBUG = True

    # Recently, it because required somehow that the DB path is an absolute path
    DB_NAME = 'sandpiper_20.sqlite3'
    LYRA_DB_PATH = 'sqlite:///'+os.path.join(os.path.dirname(__file__), '../db/{}'.format(DB_NAME))
    PROD_DB_PATH = LYRA_DB_PATH #'sqlite:////data/{}'.format(DB_NAME)

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'running_on_lyra')):
        SQLALCHEMY_DATABASE_URI = LYRA_DB_PATH
    else:        
        ## For deployment
        SQLALCHEMY_DATABASE_URI = PROD_DB_PATH
    print("Connecting to db {}".format(SQLALCHEMY_DATABASE_URI))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True
