'''
Creates the sqlite database and populates tables by reading from CHS DVDs inserted in DVD reader.
Intent is that user will only load one CHS East and one CHS West DVD.
This forms the database. Later code will read current CHS DVDs and compare data to what is in database
to check for errors, new charts, new editions, charts withdrawn and potential errors.

Intent later is to modify this code to also read from a .zip file (this is how the monthly data is received).

'''

import os
import common_utils as utils
from datetime import datetime

class RunChecker():

    def __init__(self, database_signals, checker_data_input_path, run_checker_conn, run_checker_cursor):
        # Create an instance of CreateDatabaseSignals
        self.database_signals = database_signals
        # establish where the cursors are in the database
        self.create_database_conn = run_checker_conn
        self.create_database_cursor = run_checker_cursor
        # database data input path
        self.input_data_path = checker_data_input_path

    def create_database(self, text_browser_widget):
        utils.update_text_browser(text_browser_widget, "\nMade it!")


if __name__ == "__main__":
    pass
