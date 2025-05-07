# à lancer depuis le rep Project pour avoir Project/data/CleanMap_DB.db

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


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)



def main():
    database = "data/CleanMap_DB.db" # depuis le rep Project

    TABLE_locations = """
CREATE TABLE IF NOT EXISTS locations  
(   location_id INTEGER NOT NULL DEFAULT 0,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    clean_status VARCHAR(40),
    last_cleaned_date TEXT,

    UNIQUE (latitude, longitude),

    PRIMARY KEY (location_id)  );"""


    TABLE_discussions = """
CREATE TABLE IF NOT EXISTS discussions 
(   discussion_id INTEGER NOT NULL DEFAULT 0,
    discussion_title VARCHAR(50),
    location_id INTEGER NOT NULL,

    PRIMARY KEY (discussion_id),
            
    FOREIGN KEY(location_id)
        REFERENCES locations(location_id)
        ON DELETE CASCADE   );"""


    TABLE_messages = """
CREATE TABLE IF NOT EXISTS messages 
(   message_id INTEGER NOT NULL DEFAULT 0,
    m_datetime TEXT,
    m_text VARCHAR(1500),
    discussion_id INTEGER NOT NULL,
    username TEXT,

    PRIMARY KEY  (message_id), 
    
    FOREIGN KEY(username)
        REFERENCES users(username)
        ON DELETE CASCADE,

    FOREIGN KEY(discussion_id)
        REFERENCES discussions(discussion_id)
        ON DELETE CASCADE  );"""
    

    TABLE_users = """
CREATE TABLE IF NOT EXISTS users 
(   id INTEGER,
    username TEXT,
    password TEXT,
    email TEXT,

    PRIMARY KEY (id), 
    UNIQUE (username)   );
"""


    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_table(conn, TABLE_locations) # create locations table
        create_table(conn, TABLE_discussions) # create discussions table
        create_table(conn, TABLE_messages) # create messages table
        create_table(conn,TABLE_users) # create messages users

    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()