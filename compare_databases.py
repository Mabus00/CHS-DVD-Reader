'''
Compares the content of the master and current databases and finds new (i.e., not in master but in current) or missing (i.e., withdrawn)
(i.e., in master but not in current) tables and reports the findings on the error tab

table = folder

'''

import common_utils as utils

# Define the RunChecker class
class CompareDatabases():

    # Constructor for initializing the RunChecker object
    def __init__(self, master_database_cursor, current_database_cursor):
        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    # Function to remove indicated portion from table_name
    def remove_text(self, table_name, part_to_replace):
        parts = table_name.split('_')
        new_parts = [part for part in parts if part != part_to_replace]
        new_table_name = '_'.join(new_parts)
        return new_table_name

    def compare_databases(self):
        temp_tables_missing_in_master = []
        temp_tables_missing_in_current = []
        # Get the list of table names for both databases
        self.master_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_master = [row[0] for row in self.master_database_cursor.fetchall()]
        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]
        # extract yyyymmdd from table names to conduct comparison; only send the first entry in the table 'cause it's all you need
        master_yyyymmdd = utils.extract_yyyymmdd(tables_master[0])
        current_yyyymmdd = utils.extract_yyyymmdd(tables_current[0])
        # Apply the function to remove the yyyymmdd from the table name
        tables_master_temp = [self.remove_text(table, master_yyyymmdd) for table in tables_master]
        tables_current_temp = [self.remove_text(table, current_yyyymmdd) for table in tables_current]
        # Find tables in "master" that are not in "current" and vice versa
        tables_missing_in_current = [table for table in tables_master_temp if table not in tables_current_temp]
        tables_missing_in_master = [table for table in tables_current_temp if table not in tables_master_temp]  
        # add the yyyymmdd to match complete table name
        for i in range(len(tables_missing_in_master)):
            temp_tables_missing_in_master.append(utils.insert_text(tables_missing_in_master[i], master_yyyymmdd, pos_to_insert=1))
        # add the yyyymmdd to match complete table name
        for i in range(len(tables_missing_in_current)):
            temp_tables_missing_in_current.append(utils.insert_text(tables_missing_in_current[i], current_yyyymmdd, pos_to_insert=1))
        return tables_master_temp, temp_tables_missing_in_master, tables_current_temp, temp_tables_missing_in_current, master_yyyymmdd, current_yyyymmdd

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
