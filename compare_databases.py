'''
Compares the content of the master and current databases and finds new (i.e., not in master but in current) or missing (i.e., withdrawn)
(i.e., in master but not in current) tables and reports the findings on the error tab

table = folder

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareDatabases():

    # Constructor for initializing the RunChecker object
    def __init__(self, master_database_cursor, current_database_cursor):

        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def compare_databases(self):
        # Get the list of table names for both databases
        self.master_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_master = [row[0] for row in self.master_database_cursor.fetchall()]

        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]

        # extract yyyymmdd from table names to conduct comparison
        master_yyyymmdd = utils.extract_yyyymmdd(tables_master[0])
        current_yyyymmdd = utils.extract_yyyymmdd(tables_current[0])
        
        # Apply the function to remove the yyyymmdd from the table name
        tables_master_temp = [utils.remove_text(table, master_yyyymmdd) for table in tables_master]
        tables_current_temp = [utils.remove_text(table, current_yyyymmdd) for table in tables_current]

        # Find tables in "master" that are not in "current" and vice versa
        tables_missing_in_current = set(tables_master_temp) - set(tables_current_temp)
        tables_missing_in_master = set(tables_current_temp) - set(tables_master_temp)

        return tables_master_temp, tables_current_temp, tables_missing_in_master, tables_missing_in_current, master_yyyymmdd, current_yyyymmdd

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
