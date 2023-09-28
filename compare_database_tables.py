'''

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareDatabaseTables():

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

    def compare_database_tables(self, tables_master, tables_current, tables_missing_in_current, tables_missing_in_master):
        # tables_missing_in_current represent tables that have been removed, whereas tables_missing_in_master represent tables that have been added
        print('compare tables')
   
        # Remove tables_missing_from_master from tables_master
        tables_master = [table for table in tables_master if table not in tables_missing_in_master]

        # remove yyyymmdd from table name; not required for comparison because correct yyyymmdd has already been established
        mod_tables_master = set(utils.replace_text_with_underscore(table_name, pos_to_replace=1) for table_name in tables_master)
        mod_tables_current = set(utils.replace_text_with_underscore(table_name, pos_to_replace=1) for table_name in tables_current)
        
        # Iterate over the prefixes and compare
        for prefix in mod_tables_master:
            if prefix not in mod_tables_current:
                print(f"Prefix '{prefix}' exists in master but is missing in current.")

        
        # 3. start with master and find the same table (with the newer date) in current
        # self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
