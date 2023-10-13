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
2 EDTN
3 ISDT
4 UADT
5 Title

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class FindDataMismatches():

    # Constructor for initializing the CompareEditions object
    def __init__(self, master_database_cursor, current_database_cursor):

        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

        print('looking for mismatches')

    def find_mismatches(self, tables_master, master_yyyymmdd, current_yyyymmdd):
         # Iterate through table names in tables_master and find corresponding table in tables_current_temp
        for table_name in tables_master:
            # add the yyyymmdd to match complete table name
            temp_master_table_name = utils.insert_text(table_name, master_yyyymmdd, pos_to_insert=1)
            temp_current_table_name = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            
            # Table exists in both databases; compare content
            self.master_database_cursor.execute(f"SELECT * FROM {temp_master_table_name}")
            master_columns = [description[0] for description in self.master_database_cursor.description]

            self.current_database_cursor.execute(f"SELECT * FROM {temp_current_table_name}")
            current_columns = [description[0] for description in self.current_database_cursor.description]

            # Compare columns starting from the second column
            for i in range(1, min(len(master_columns), len(current_columns))):
                master_column = master_columns[i]
                current_column = current_columns[i]

                self.master_database_cursor.execute(f"SELECT [{master_column}] FROM {temp_master_table_name};")
                master_data = [row[0] for row in self.master_database_cursor.fetchall()]

                self.current_database_cursor.execute(f"SELECT [{current_column}] FROM {temp_current_table_name};")
                current_data = [row[0] for row in self.current_database_cursor.fetchall()]

            # Compare data and report any mismatches
            if master_data != current_data:
                # Compare data and report any mismatches
                for row_number, (master_value, current_value) in enumerate(zip(master_data, current_data), start=1):
                    if master_value != current_value:
                        print(f"Mismatch in table '{table_name}', column '{master_column}' at row {row_number}.")



# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
