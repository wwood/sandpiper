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
        DB_NAME = 'sandpiper_21_test.duckdb'
    else:
        print("Running in DB production mode")
        # Open read-only to avoid database lock issues.
        DB_NAME = 'sandpiper_35.duckdb?access_mode=READ_ONLY'
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
    # Avoid explicit ROLLBACK statements when using DuckDB in read-only mode so
    # graceful shutdowns are not delayed by unnecessary transaction cleanup.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "isolation_level": "AUTOCOMMIT",
        "connect_args": {"read_only": True},
    }
