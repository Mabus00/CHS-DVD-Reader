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
   
        # Remove tables_missing_from_current from tables_master; these are tables that have been removed
        tables_master = [table for table in tables_master if table not in tables_missing_in_current]

        # extract yyyymmdd from table names to conduct comparison
        self.master_yyyymmdd = utils.extract_yyyymmdd(tables_master[0])
        self.current_yyyymmdd = utils.extract_yyyymmdd(tables_current[0])

        # remove yyyymmdd from table name; not required for comparison because correct yyyymmdd has already been established
        tables_master_temp = [utils.remove_text(table, self.master_yyyymmdd) for table in tables_master]
        tables_current_temp = [utils.remove_text(table, self.current_yyyymmdd) for table in tables_current]

        # Iterate through table names in tables_master_temp and find corresponding table in tables_current_temp
        for table_name in tables_master_temp:
            if table_name in tables_current_temp:
                # add the yyyymmdd to match complete table name
                temp_master_table_name = utils.insert_text(table_name, self.master_yyyymmdd, pos_to_insert=1)
                temp_current_table_name = utils.insert_text(table_name, self.current_yyyymmdd, pos_to_insert=1)
                
                # Table exists in both databases; compare content
                self.master_database_cursor.execute(f"SELECT * FROM {temp_master_table_name}")
                master_data = self.master_database_cursor.fetchall()

                self.current_database_cursor.execute(f"SELECT * FROM {temp_current_table_name}")
                current_data = self.current_database_cursor.fetchall()

                # Get the index of the "chart" column (first column)
                chart_column_index = 0

                # Create a set of chart names from current_data for faster lookup
                current_chart_names = set(row[chart_column_index] for row in current_data)

                # Iterate through rows of master_data
                for i, row in enumerate(master_data):
                    chart_name = row[chart_column_index]

                    # Check if the chart name from master_data is not in current_data
                    if chart_name not in current_chart_names:
                        # Print the table name
                        print(f"Differences found in table: {temp_current_table_name}")

                        # Print the chart name that is missing in current_data
                        print(f"Chart name missing in current_data at Row {i + 1}: {chart_name}")

                
        # 3. start with master and find the same table (with the newer date) in current
        # self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
