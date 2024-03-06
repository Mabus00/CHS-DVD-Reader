'''
Compares the master_database and current_database chart numbers in mathcing tables (tables = folders) and 
reports on:
1. charts withdrawn - charts that exist in the master_database but are not in the current_database.
2. new charts - charts that don't exist in the master_database but do exist in the current_database.

Note - either of the above conditions can also be considered errors on the CHS DVD which is why the user 
needs to accept the indicated reports before moving on and updating the master_database with the current_database.

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareChartNumbers():

    # Constructor for initializing the RunChecker object
    def __init__(self, master_database_cursor, current_database_cursor):

        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def compare_chart_numbers(self, tables_master, master_yyyymmdd, current_yyyymmdd):

        charts_withdrawn_result = []
        new_charts_result = []

        # Iterate through table names in tables_master and find corresponding table in tables_current_temp
        for table_name in tables_master:
            # add the yyyymmdd to match complete table name
            temp_master_table_name = utils.insert_text(table_name, master_yyyymmdd, pos_to_insert=1)
            temp_current_table_name = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            
            # table_name exists in both databases; compare content
            self.master_database_cursor.execute(f"SELECT * FROM {temp_master_table_name}")
            master_data = self.master_database_cursor.fetchall()

            self.current_database_cursor.execute(f"SELECT * FROM {temp_current_table_name}")
            current_data = self.current_database_cursor.fetchall()

            # Set the index of the table column (first column = chart number)
            chart_column_index = 1

            result = utils.detect_column_changes(chart_column_index, master_data, current_data, temp_current_table_name)
            charts_withdrawn_result.extend(result for result in [result] if result)

            result = utils.detect_column_changes(chart_column_index, current_data, master_data, temp_current_table_name)
            new_charts_result.extend(result for result in [result] if result)

        return charts_withdrawn_result, new_charts_result

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
