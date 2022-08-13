import psycopg2
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
conn = psycopg2.connect(host='localhost', user='postgres', password='root', dbname='fyyurdb', port=5432)

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/fyyurdb'
