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

    def __init__(self, database_signals, master_database_name, master_database_conn, master_database_cursor, current_database_name, current_database_conn, current_database_cursor, runCheckerTextBrowser):
        # Create an instance of CreateDatabaseSignals
        self.database_signals = database_signals
        # establish database names, connections and cursors
        self.master_database_name = master_database_name
        self.master_database_conn = master_database_conn
        self.master_database_cursor = master_database_cursor
        self.current_database_name = current_database_name
        self.current_database_conn = current_database_conn
        self.current_database_cursor = current_database_cursor
        self.text_browser_widget = runCheckerTextBrowser

    def compare_databases(self):
        # Get the current year and month in the format "YYYYMM"
        # current_year_month = datetime.now().strftime('%Y%m')

        # Initialize a list to store matching foldernames
        #matching_foldernames = []
        # Loop through the foldernames and check for matching current year and data
        #for foldername in foldernames:
            #if current_year_month in foldername:
            #matching_foldernames.append(foldername)

        ''' STEPS '''
        # from chs_dvd_reader_main both databases were opened




        # 2. compare the DTG of the master database to current database; ensure the current is at least one month newer than the master; if more confirm with user
        # 3. start with master and find the same table (with the newer date) in current
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.
        # 7. add the ability to print the result as a pdf.
        # 8. once all has been verified and the user is happy, overwrite the master with the current.

        print('run_checker')


if __name__ == "__main__":
    pass
