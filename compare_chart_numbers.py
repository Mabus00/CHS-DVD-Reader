'''
Compares the master_database and current_database chart numbers in mathcing tables (tables = folders) and 
reports on:
1. charts withdrawn - charts that exist in the master_database but are not in the current_database.
2. new charts - charts that don't exist in the master_database but do exist in the current_database.

Note - either of the above conditions can also be considered errors on the CHS DVD which is why the user 
needs to accept the indicated reports before moving on and updating the master_database with the current_database.

'''

import common_utils as utils

# Define the RunChecker class
class CompareChartNumbers():

    # Constructor for initializing the RunChecker object
    def __init__(self, master_database_cursor, current_database_cursor):
        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def detect_column_changes(self, column_index, base_table, secondary_table, table_name):
        # using the column_index to identify the comparator, detect changes in cell content (i.e., missing cell content)
        # base_table = primary table against which the secondary_table is being compared
        # reset encountered column content
        encountered_column_content = []
        # Create a list of tuples containing (row_index, cell_content) from secondary_table for comparison
        column_content = [(i, row[column_index].strip()) for i, row in enumerate(secondary_table)]
        # Initialize a list to store the rows where missing cell content has been found
        found_rows = []
        # Iterate through rows of base_table
        for i, row in enumerate(base_table):
            # get base_table cell content for the current row
            cell_content = row[column_index].strip()
            # Check if the cell content from base_table is not in secondary_table
            if (cell_content not in [content[1] for content in column_content]) and (cell_content not in [content[1] for content in encountered_column_content]):
                # Append the row to the list
                found_rows.append(row)
            # whether or not above condition fails add it to encountered_column_content so we don't keep checking repeating cell content
            if cell_content not in [content[1] for content in encountered_column_content]:
                # Add the cell content to the encountered_column_content list
                encountered_column_content.append((i, cell_content))
        # returns a tuple consisting of the table_name and a list of tuples with the row data
        return (table_name, found_rows) if found_rows else None

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
            result = self.detect_column_changes(chart_column_index, master_data, current_data, temp_current_table_name)
            charts_withdrawn_result.extend(result for result in [result] if result)
            result = self.detect_column_changes(chart_column_index, current_data, master_data, temp_current_table_name)
            new_charts_result.extend(result for result in [result] if result)
        return charts_withdrawn_result, new_charts_result

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
