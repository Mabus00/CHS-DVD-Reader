# Import necessary modules
import common_utils as utils
from datetime import datetime

# Define the RunChecker class
class RunChecker():

    # Constructor for initializing the RunChecker object
    def __init__(self, run_checker_textbox, errors_textbox, master_database_name, master_database_conn, master_database_cursor, current_database_name, current_database_conn, current_database_cursor, runCheckerTextBrowser):
        # Create an instance of CreateDatabaseSignals (not shown in code, assuming it's an imported class)
        self.run_checker_textbox = run_checker_textbox
        self.errors_textbox = errors_textbox

        # Establish database names, connections, and cursors
        self.master_database_name = master_database_name
        self.master_database_conn = master_database_conn
        self.master_database_cursor = master_database_cursor
        self.current_database_name = current_database_name
        self.current_database_conn = current_database_conn
        self.current_database_cursor = current_database_cursor
        self.text_browser_widget = runCheckerTextBrowser

        self.master_yyyymmdd = ''
        self.current_yyyymmdd = ''

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
                self.run_checker_textbox.emit("\nThe Master and Current databases are in compliance with the date matching criteria. ")
                break  # Exit the loop if both conditions are True
            else:
                self.run_checker_textbox.emit("\nThe Master and Current databases are not in compliance with the date matching criteria. Please review the results and address the indicated issues.")
                return

        # 3. start with master and find the same table (with the newer date) in current
        self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.
        # 7. add the ability to print the result as a pdf.
        # 8. once all has been verified and the user is happy, overwrite the master with the current.

        # Print a message to indicate that the checker has run
        print('The Checker ran succesfully!')

    def get_databases_yyyymmdd(self, table_prefixes):
        # Initialize dictionaries to store dates found in each database
        master_dates = {}
        current_dates = {}
        # get the first yyyymmdd prefix of each table in each database
        for prefix in table_prefixes:
            # Get the yyyymmdd from the first table in the master database
            self.master_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, self.master_database_conn)
            if self.master_yyyymmdd is not None:
                master_dates[prefix] = self.master_yyyymmdd
            # Get the yyyymmdd from the first table in the current database
            self.current_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, self.current_database_conn)
            if self.current_yyyymmdd is not None:
                current_dates[prefix] = self.current_yyyymmdd
        return master_dates, current_dates

    def compare_tables_east_west_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix of each table in each database and ensure they match within the database
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
        # compare the yyyymmdd prefix of the EastDVD in each database and ensure the current database is at least a month older than the master database
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

    # Function to replace text between the first and second underscores with one underscore
    def replace_text_with_underscore(self, table_name):
        parts = table_name.split('_')
        return parts[0] + '_' + '_'.join(parts[2:])
    
    def replace_underscore_with_text(self, table_name, yyyymmdd):
        parts = table_name.split('_')
        return '_'.join([parts[0], yyyymmdd] + parts[1:])  # Join all parts with underscores

    def compare_database_content(self):
        # Get the list of table names for both databases
        self.master_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_master = [row[0] for row in self.master_database_cursor.fetchall()]

        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]
       
        # Apply the function to remove the text between the first and second underscores
        tables_master_temp = [self.replace_text_with_underscore(table) for table in tables_master]
        tables_current_temp = [self.replace_text_with_underscore(table) for table in tables_current]

        # Find tables in "master" that are not in "current" and vice versa
        tables_missing_in_current = set(tables_master_temp) - set(tables_current_temp)
        tables_missing_in_master = set(tables_current_temp) - set(tables_master_temp)

        # Print tables that are not matching between "master" and "current"
        if tables_missing_in_current:
            self.run_checker_textbox.emit("\nErrors were noted - see the Errors Tab")
            self.errors_textbox.emit("Tables missing in 'current' but present in 'master':")
            for table in tables_missing_in_current:
                temp = self.replace_underscore_with_text(table, self.current_yyyymmdd)
                self.errors_textbox.emit(temp)

        if tables_missing_in_master:
            self.run_checker_textbox.emit("\nErrors were noted - see the Errors Tab")
            self.errors_textbox.emit("\nTables missing in 'master' but present in 'current':")
            for table in tables_missing_in_master:
                temp = self.replace_underscore_with_text(table, self.master_yyyymmdd)
                self.errors_textbox.emit(temp)

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
