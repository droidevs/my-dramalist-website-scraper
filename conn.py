# This file will handle the database connection.
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

conn = create_connection("database.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS dramas (
    drama_id INTEGER PRIMARY KEY,      -- MDL ID (e.g. 49231)
    title TEXT,
    native_title TEXT,
    aka_titles TEXT,
    year INTEGER,
    country TEXT,
    type TEXT,
    episodes INTEGER,
    duration TEXT,
    rating REAL,
    ranked INTEGER,
    popularity INTEGER,
    content_rating TEXT,
    description TEXT,
    url TEXT UNIQUE
);
""")

cur = conn.cursor()