"""
    config.py
    - settings for the flask application object
"""
import os

class BaseConfig:
    DEBUG = True

    # Recently, it because required somehow that the DB path is an absolute path
    # Check if we're in testing mode
    if os.environ.get('SANDPIPER_TESTING'):
        print("Running in DB testing mode")
        DB_NAME = 'sandpiper_39_test.duckdb'
    else:
        print("Running in DB production mode")
        # Open read-only to avoid database lock issues.
        DB_NAME = 'sandpiper_39.duckdb'
    LYRA_DB_PATH = 'duckdb:///'+os.path.join(os.path.dirname(__file__), '../db/{}'.format(DB_NAME))
    # LYRA_DB_PATH = 'duckdb:////scratch/sandpiper/sandpiper_33.duckdb'
    # LYRA_DB_PATH = 'duckdb:////scratch/sandpiper/sandpiper_19_test.duckdb'
    PROD_DB_PATH = LYRA_DB_PATH #'duckdb:////data/{}'.format(DB_NAME)

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'running_on_lyra')):
        SQLALCHEMY_DATABASE_URI = LYRA_DB_PATH
    else:        
        ## For deployment
        SQLALCHEMY_DATABASE_URI = PROD_DB_PATH
    print("Connecting to db {}".format(SQLALCHEMY_DATABASE_URI))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True
    # Set as read-only to avoid locking issues unless we are loading it with data
    if not os.environ.get('SANDPIPER_LOADING_DATA'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"read_only": True}
        }