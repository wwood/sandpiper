"""
    config.py
    - settings for the flask application object
"""
import os

class BaseConfig:
    DEBUG = True

    LYRA_DB_PATH = 'sqlite:////home/woodcrob/git/sandpiper/backend/sra_20211215.mach3.sandpiper12.sqlite3'

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'running_on_lyra')):
        SQLALCHEMY_DATABASE_URI = LYRA_DB_PATH
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///6_runs.sandpiper.sqlite3'

    else:
        ## For local testing
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///6_runs.sandpiper.sqlite3'

        ## For lyra testing
        # SQLALCHEMY_DATABASE_URI = LYRA_DB_PATH
        
        ## For deployment
        SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sra_20211215.mach3.sandpiper12.sqlite3'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True
