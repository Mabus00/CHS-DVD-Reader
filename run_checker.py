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
        # Get the current year and month in the format "YYYYMM"
        # current_year_month = datetime.now().strftime('%Y%m')

        # Initialize a list to store matching foldernames (code commented out)
        #matching_foldernames = []

        ''' STEPS '''

        # Call the compare_tables method to perform table comparison
        result = self.compare_tables()
        print(result)
        # Compare the DTG of the master database and the current database; ensure the current is at least one month newer than the master; if more, confirm with the user
        # Get the table names from the master database

    def compare_tables(self):
        table_prefixes = ['EastDVD', 'WestDVD']
        
        match_result, month_result = False, False

        # Initialize dictionaries to store dates found in each database
        master_dates = {}
        current_dates = {}

        # Loop through the table prefixes and compare dates
        for prefix in table_prefixes:
            # Get the yyyymmdd from the first table in the master database
            master_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, self.master_database_conn)
            if master_yyyymmdd is not None:
                master_dates[prefix] = master_yyyymmdd

            # Get the yyyymmdd from the first table in the current database
            current_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, self.current_database_conn)
            if current_yyyymmdd is not None:
                current_dates[prefix] = current_yyyymmdd

        # Compare the EastDVD and WestDVD tables separately for both master and current databases
        if (
            master_dates.get('EastDVD') == master_dates.get('WestDVD') and
            current_dates.get('EastDVD') == current_dates.get('WestDVD') and
            datetime.strptime(current_dates.get('EastDVD'), '%Y%m%d').month > datetime.strptime(master_dates.get('EastDVD'), '%Y%m%d').month
            ):
                match_result, month_result = True, True

        return match_result, month_result

        
        # Additional steps for the comparison process (commented out)
        # 3. start with master and find the same table (with the newer date) in current
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.
        # 7. add the ability to print the result as a pdf.
        # 8. once all has been verified and the user is happy, overwrite the master with the current.

        # Print a message to indicate that the checker has run
        print('run_checker')

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
