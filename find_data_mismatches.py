'''
Compare content of remaining tables (folders) and find mismatches (i.e., new editions, potential errors)
in columns beyond column 1 (chart number).

The message generated will depend on which column the mismatch is found in.

Raster table columns:
0 Chart 
1 File
2 Edn Date
3 Last NTM
4 Edn#
5 Title

Vector table columns:
0 Chart
1 ENC
2 EDTN.UPDN = Edition Number.Update Number
3 ISDT = Issue Date
4 UADT = Update Application Date
5 Title

'''

# Import necessary modules
import common_utils as utils
from datetime import datetime

# Define the RunChecker class
class FindDataMismatches():

    # Constructor for initializing the CompareEditions object
    def __init__(self, master_database_cursor, current_database_cursor):

        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

        self.raster_table_columns = ['Chart', 'File', 'Edn Date', 'Last NTM', 'Edn#', 'Title']

        self.vector_table_columns = ['Chart','ENC','EDTN','ISDT','UADT','Title']

        print('looking for mismatches')

    def find_mismatches(self, tables_master, master_yyyymmdd, current_yyyymmdd):
        new_editions = []
        errors = []

         # Iterate through table names in tables_master and find corresponding table in tables_current_temp
        for table_name in tables_master:
            # add the yyyymmdd to match complete table name
            temp_master_table_name = utils.insert_text(table_name, master_yyyymmdd, pos_to_insert=1)
            temp_current_table_name = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            
            # Table exists in both databases; compare content
            self.master_database_cursor.execute(f"SELECT * FROM {temp_master_table_name}")
            master_data = self.master_database_cursor.fetchall()

            self.current_database_cursor.execute(f"SELECT * FROM {temp_current_table_name}")
            current_data = self.current_database_cursor.fetchall()

            # Define the index of the second column (file name)
            second_column_index = 1  # Assuming 0-based index

            # Initialize a list to new charts and store missing chart numbers
            found_charts = []
            found_errors = []

            # Iterate through rows in the master table
            for master_row_number, master_row in enumerate(master_data, start=1):
                # Extract the file name from the master row
                master_file_name = master_row[second_column_index]

                # Find the corresponding row in the current table using the file name
                matching_current_row = None
                for current_row_number, current_row in enumerate(current_data, start=1):
                    if current_row[second_column_index] == master_file_name:
                        matching_current_row = current_row
                        break

                # If a matching row is found, compare the content of the remaining four columns
                if matching_current_row:
                    for i in range(2, len(master_row)):  # Start from the third column (0-based index)
                        master_value = master_row[i]
                        current_value = matching_current_row[i]

                        is_date = utils.is_valid_date(master_value)
                        if is_date:
                            master_value, current_value = utils.convert_date_for_comparison(master_value, current_value)

                        if master_value != current_value:
                            if current_value > master_value:
                                    found_charts.append((master_row[second_column_index], matching_current_row[i]))
                            else:
                                found_errors.append((master_row[second_column_index], matching_current_row[i]))

                            # RIGHT HERE - BUILD TABLES OF INFORMATION FOR RETURN THEN TO COMMON_UTILS
                            if "RM" in table_name:
                                print(f"'{table_name}', '{master_file_name}', '{self.raster_table_columns[i]}' = '{master_row[i]}' ->  '{matching_current_row[i]}', master row {master_row_number} / current row {current_row_number}.")
                            else:
                                print(f"'{table_name}', '{master_file_name}', '{self.vector_table_columns[i]}' = '{master_row[i]}' ->  '{matching_current_row[i]}', master row {master_row_number} / current row {current_row_number}.")
            if found_charts:
                new_editions.append((table_name, found_charts))
            if found_errors:
                errors.append((table_name, found_errors))

        return new_editions, errors

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
