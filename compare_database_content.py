'''
Compares the master and current database table names to see if any are new or missing and reports the findings on the error tab.

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareDatabases():

    # Constructor for initializing the RunChecker object
    def __init__(self, run_checker_textbox, errors_textbox, master_database_cursor, current_database_cursor):
        # Create an instance of CreateDatabaseSignals (not shown in code, assuming it's an imported class)
        self.run_checker_textbox = run_checker_textbox
        self.errors_textbox = errors_textbox

        # Establish database names, connections, and cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

        self.master_yyyymmdd = ''
        self.current_yyyymmdd = ''

    def compare_database_content(self):
        # Get the list of table names for both databases
        self.master_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_master = [row[0] for row in self.master_database_cursor.fetchall()]

        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]
       
        # Apply the function to remove the text between the first and second underscores
        tables_master_temp = [utils.replace_text_with_underscore(table) for table in tables_master]
        tables_current_temp = [utils.replace_text_with_underscore(table) for table in tables_current]

        # Find tables in "master" that are not in "current" and vice versa
        tables_missing_in_current = set(tables_master_temp) - set(tables_current_temp)
        tables_missing_in_master = set(tables_current_temp) - set(tables_master_temp)

        # Print tables that are not matching between "master" and "current"
        if tables_missing_in_current:
            self.run_checker_textbox.emit("\nErrors were noted - see the Errors Tab")
            self.errors_textbox.emit("Tables missing in 'current' but present in 'master':")
            for table in tables_missing_in_current:
                temp = utils.replace_underscore_with_text(table, self.current_yyyymmdd)
                self.errors_textbox.emit(temp)

        if tables_missing_in_master:
            self.run_checker_textbox.emit("\nErrors were noted - see the Errors Tab")
            self.errors_textbox.emit("\nTables missing in 'master' but present in 'current':")
            for table in tables_missing_in_master:
                temp = utils.replace_underscore_with_text(table, self.master_yyyymmdd)
                self.errors_textbox.emit(temp)

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
