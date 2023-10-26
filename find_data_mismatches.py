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
        misc_findings = []

        # Iterate through table names in tables_master and find corresponding table in tables_current_temp
        for table_name in tables_master:
            # add the yyyymmdd to match the complete table name
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
            found_new_edition = []
            misc_finding = []

            # Iterate through rows in the master table
            for master_row in master_data:
                # Extract the file name from the master row
                master_file_name = master_row[second_column_index]

                # Find the corresponding row in the current table using the file name
                matching_current_row = None
                for current_row in current_data:
                    if current_row[second_column_index] == master_file_name:
                        matching_current_row = current_row
                        break

                # If a matching row is found, compare the content of the remaining columns
                if matching_current_row:
                    master_content = master_row[2:]  # Get the content of columns 2-4
                    current_content = matching_current_row[2:]  # Get the content of columns 2-4 in current_value

                    is_date = all(utils.is_valid_date(value) for value in master_content)
                    if is_date:
                        master_content, current_content = zip(*[utils.convert_date_for_comparison(master, current)
                                                                for master, current in zip(master_content, current_content)])

                    if master_content[:3] != current_content[:3]:
                        found_new_edition.append((master_row[second_column_index], matching_current_row[2:]))

                    if master_content[3] != current_content[3]:
                        misc_finding.append((master_row[second_column_index], matching_current_row[2:]))

            if found_new_edition:
                new_editions.append((table_name, found_new_edition))
            if misc_finding:
                misc_findings.append((table_name, misc_finding))

        return new_editions, misc_findings


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
