'''
Does the basic checks to ensure:
1. the East and West tables in each of the master and current databases have the same date; this to ensure the tables were created correctly.
2. the new current database is at least one month older than the master database; this to ensure the comparison between databases is valid.

If all good returns True and the process continues

Updated to streamline.

'''

# Import necessary modules
import os
import common_utils as utils
from datetime import datetime

# Define the RunChecker class
class RunChecker():

    # Constructor for initializing the RunChecker object
    def __init__(self, current_database_name, run_checker_textbox, errors_textbox, database_input_path):
        self.current_database_name = current_database_name
        # Create an instance of CreateDatabaseSignals (not shown in code, assuming it's an imported class)
        self.run_checker_textbox = run_checker_textbox
        self.errors_textbox = errors_textbox

        # database data input path
        self.input_data_path = database_input_path

    def pre_build_checks(self):
        path_selected = True
        
        # delete if necessary then build new current database
        # NOTE UNCOMMENT FOR PRODUCTION ONLY
        if os.path.exists(self.current_database_name):
            utils.delete_existing_database(self.current_database_name, self.run_checker_textbox)

        # ensure user has selected a data input path
        if not utils.confirm_data_path(self.input_data_path):
            path_selected = False
        
        return path_selected
    
    # Method to compare databases
    def confirm_database_compliance(self, master_database_conn, current_database_conn):
        # Define table prefixes to be compared
        table_prefixes = ['EastDVD', 'WestDVD']
        # get the yyyymmdd for THE FIRST TABLE in both databases to conduct following two checks
        master_dates, current_dates = self.get_databases_yyyymmdd(master_database_conn, current_database_conn, table_prefixes)
        # Call the compare_tables_east_west_dates and compare_database_dates methods to perform table and databases comparisons
        match_result = self.compare_tables_east_west_dates(master_dates, current_dates)
        month_result = self.compare_database_dates(master_dates, current_dates)
        if match_result and month_result:
            self.run_checker_textbox.emit("\nThe Master and Current databases are in compliance with the date matching criteria. ")
            return True
        else:
            self.run_checker_textbox.emit("\nThe Master and Current databases are not in compliance with the date matching criteria. Please review the results and address the indicated issues.")
            return False

    def get_databases_yyyymmdd(self, master_database_conn, current_database_conn, table_prefixes):
        # Initialize dictionaries to store dates found in each database
        master_dates = {}
        current_dates = {}
        # get the first yyyymmdd prefix of each table in each database
        for prefix in table_prefixes:
            # Get the yyyymmdd from the first table in the master database
            master_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, master_database_conn)
            if master_yyyymmdd is not None:
                master_dates[prefix] = master_yyyymmdd
            # Get the yyyymmdd from the first table in the current database
            current_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, current_database_conn)
            if current_yyyymmdd is not None:
                current_dates[prefix] = current_yyyymmdd
        return master_dates, current_dates

    def compare_tables_east_west_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix from THE FIRST TABLE in each database and ensure they match within the database
        match_result = False
        # Compare the EastDVD and WestDVD tables separately for both master and current databases
        if (
            master_dates.get('EastDVD') == master_dates.get('WestDVD') and
            current_dates.get('EastDVD') == current_dates.get('WestDVD')
        ):
            self.run_checker_textbox.emit("\nEast & West DVD dates match within one or both databases.")
            match_result = True
        else:
            self.run_checker_textbox.emit("\nEast & West DVD dates do not match within one or both databases.")
        return match_result

    def compare_database_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix from THE FIRST TABLE of the EastDVD in each database and ensure the current database is at least a month older than the master database
        # only using EastDVD because the compare_tables_east_west_dates check comfirmed they're the same
        month_result = False
        # Compare the EastDVD tables separately for both master and current databases
        master_date = datetime.strptime(master_dates.get('EastDVD'), '%Y%m%d')
        current_date = datetime.strptime(current_dates.get('EastDVD'), '%Y%m%d')
        if current_date.month > master_date.month:
            self.run_checker_textbox.emit("\nCurrent East & West DVD dates are a month or more later than the Master Database dates.")
            month_result = True
        else:
            self.run_checker_textbox.emit("\nCurrent East & West DVD dates are not a month or more later than the Master Database dates.")
        return month_result

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
