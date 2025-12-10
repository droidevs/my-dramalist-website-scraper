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

conn.execute("""
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY,       -- MDL tag id (from "th=" in link)
    name TEXT UNIQUE
);
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS drama_tags (
    drama_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (drama_id, tag_id),
    FOREIGN KEY (drama_id) REFERENCES dramas(drama_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);
""")

cur = conn.cursor()