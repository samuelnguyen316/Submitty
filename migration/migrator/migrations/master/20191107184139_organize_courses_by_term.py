"""Migration for the Submitty master database."""

import re
from pprint import pprint

def up(config, database):
    """
    Run up migration.

    :param config: Object holding configuration details about Submitty
    :type config: migrator.config.Config
    :param database: Object for interacting with given database for environment
    :type database: migrator.db.Database
    """

    # Create terms table
    database.execute("""
CREATE TABLE IF NOT EXISTS terms (
    term_id character varying(255) PRIMARY KEY,
    name character varying(255) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    CONSTRAINT terms_check CHECK (end_date > start_date)
);""")

    # Retrieve DISTINCT set of term codes from courses table.
    # These codes need to be INSERTed before creating the FK referencing terms table.
    database.execute("SELECT DISTINCT semester FROM courses ORDER BY semester ASC;")
    term_codes = database.fetchall()

    # INSERT term codes into new terms table.
    # 1. ask sysadmin for name for each term.
    #   a. suggest that sXX = "Spring 20XX".
    #   b. suggest that fXX = "Fall 20XX".
    #   c. suggest that uXX = "Summer 20XX".
    #   d. Do not suggest anything if code is not 'f', 's', or 'u' + "XX".
    # 2. ask sysadmin for start/end dates for each term.
    #   a. suggest that sXX = 01/02/XX to 05/30/XX.
    #   b. suggest that fXX = 09/01/XX to 12/23/XX.
    #   c. suggest that uXX = 06/01/XX to 08/31/XX.
    #   d. Do not suggest anything if code is not 'f', 's', or 'u' + "XX".

    for code in term_codes:
        if re.fullmatch("^[fsu]\d{2}$", code):
            if code[0:1] == "f":
                suggested_name = "Fall 20" + code[1:3]
                suggested_start_date = "09/01/" + code[1:3]
                suggested_end_date = "12/23/" + code[1:3]
            elif code[0:1] == "s":
                suggested_name = "Spring 20" + code[1:3]
                suggested_start_date = "01/02/" + code[1:3]
                suggested_end_date = "05/30/" + code[1:3]
            else:
                suggested_name = "Summer 20" + code[1:3]
                suggested_start_date = "06/01/" + code[1:3]
                suggested_end_date = "08/31/" + code[1:3]
        else:
            suggested_name = None
            suggested_start_date = None
            suggested_end_date = None


    # Create FK, courses table (semester) references terms table (term_id)
    try:
        database.execute("ALTER TABLE ONLY courses ADD CONSTRAINT courses_fkey FOREIGN KEY (semester) REFERENCES terms (term_id) ON UPDATE CASACADE;")
    except EXCEPTION as e:
        raise SystemExit("Error creating FK: courses(semester) references terms(term_id)\n" + str(e))

def down(config, database):
    """
    Run down migration (rollback).

    :param config: Object holding configuration details about Submitty
    :type config: migrator.config.Config
    :param database: Object for interacting with given database for environment
    :type database: migrator.db.Database
    """
    pass
