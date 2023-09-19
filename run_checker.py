# Import necessary modules
import common_utils as utils
from datetime import datetime

# Define the RunChecker class
class RunChecker():

    # Constructor for initializing the RunChecker object
    def __init__(self, database_signals, master_database_name, master_database_conn, master_database_cursor, current_database_name, current_database_conn, current_database_cursor, runCheckerTextBrowser):
        # Create an instance of CreateDatabaseSignals (not shown in code, assuming it's an imported class)
        self.database_signals = database_signals

        # Establish database names, connections, and cursors
        self.master_database_name = master_database_name
        self.master_database_conn = master_database_conn
        self.master_database_cursor = master_database_cursor
        self.current_database_name = current_database_name
        self.current_database_conn = current_database_conn
        self.current_database_cursor = current_database_cursor
        self.text_browser_widget = runCheckerTextBrowser

    # Method to compare databases
    def compare_databases(self):
        # Define table prefixes to be compared
        table_prefixes = ['EastDVD', 'WestDVD']
        # get the yyyymmdd for both databases to conduct following two checks
        master_dates, current_dates = self.get_databases_yyyymmdd(table_prefixes)
        # Call the compare_tables_east_west_dates and compare_database_dates methods to perform table and databases comparisons
        while True:
            match_result = self.compare_tables_east_west_dates(master_dates, current_dates)
            month_result = self.compare_database_dates(master_dates, current_dates)
            if match_result and month_result:
                utils.update_text_browser(self.text_browser_widget, "\nThe Master and Current databases are in compliance with the date matching criteria. ")
                break  # Exit the loop if both conditions are True
            else:
                utils.update_text_browser(self.text_browser_widget, "\nThe Master and Current databases are not in compliance with the date matching criteria. Please review the results and address the indicated issues.")
                return

        
        # Additional steps for the comparison process (commented out)
        # 3. start with master and find the same table (with the newer date) in current
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.
        # 7. add the ability to print the result as a pdf.
        # 8. once all has been verified and the user is happy, overwrite the master with the current.

        # Print a message to indicate that the checker has run
        print('The Checker ran succesfully!')

        # Compare the DTG of the master database and the current database; ensure the current is at least one month newer than the master; if more, confirm with the user
        # Get the table names from the master database

    def get_databases_yyyymmdd(self, table_prefixes):
        # Initialize dictionaries to store dates found in each database
        master_dates = {}
        current_dates = {}
        # get the first yyyymmdd prefix of each table in each database
        for prefix in table_prefixes:
            # Get the yyyymmdd from the first table in the master database
            master_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, self.master_database_conn)
            if master_yyyymmdd is not None:
                master_dates[prefix] = master_yyyymmdd
            # Get the yyyymmdd from the first table in the current database
            current_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, self.current_database_conn)
            if current_yyyymmdd is not None:
                current_dates[prefix] = current_yyyymmdd
        return master_dates, current_dates

    def compare_tables_east_west_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix of each table in each database and ensure they match within the database
        match_result = False
        # Compare the EastDVD and WestDVD tables separately for both master and current databases
        if (
            master_dates.get('EastDVD') == master_dates.get('WestDVD') and
            current_dates.get('EastDVD') == current_dates.get('WestDVD')
        ):
            utils.update_text_browser(self.text_browser_widget, "\nEast & West DVD dates match within one or both databases.")
            match_result = True
        else:
            utils.update_text_browser(self.text_browser_widget, "\nEast & West DVD dates do not match within one or both databases.")
        return match_result

    def compare_database_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix of the EastDVD in each database and ensure the current database is at least a month older than the master database
        # only using EastDVD because the compare_tables_east_west_dates check comfirmed they're the same
        month_result = False
        # Compare the EastDVD tables separately for both master and current databases
        master_date = datetime.strptime(master_dates.get('EastDVD'), '%Y%m%d')
        current_date = datetime.strptime(current_dates.get('EastDVD'), '%Y%m%d')
        if current_date.month > master_date.month:
            utils.update_text_browser(self.text_browser_widget, "\nCurrent East & West DVD dates are a month or more later than the Master Database dates.")
            month_result = True
        else:
            utils.update_text_browser(self.text_browser_widget, "\nCurrent East & West DVD dates are not a month or more later than the Master Database dates.")
        return month_result


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
