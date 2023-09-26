'''
Does the basic checks to ensure:
1. the East and West tables in each of the master and current databases have the same date; this to ensure the tables were created correctly.
2. the new current database is at least one month older than the master database; this to ensure the comparison between databases is valid.

If all good returns True and the process continues

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareTables():

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

    def compare_database_tables(self):
        # Get the list of table names for both databases
        print('compare tables')

        
        # 3. start with master and find the same table (with the newer date) in current
        # self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
