'''
Compare content of remaining tables (folders) and find mismatches (i.e., new editions, potential errors)
in columns beyond column 1 (chart number).

The message generated will depend on which column the mismatch is found in.

Raster table columns:
0 BSB Chart 
1 File
2 Edition Date (yyyymmdd)
3 Last NTM (yyyymmdd)
4 Raster Edition
5 KAP Files
6 Region
7 Title

Vector table columns:
0 Collection
1 Cell Name
2 EDTN = Edition Number
3 UPDN = Update Number
4 ISDT = Issue Date (dd-Mmm-yyyy)
5 UADT = Update Application Date (dd-Mmm-yyyy)
6 SLAT = Southern Lattitude
7 WLON = Western Longitude
8 NLAT= Northern Lattitude
9 ELON = Eastern Longitude
10 Title

'''
import common_utils as utils
from datetime import datetime

# Define the FindDataMismatches class
class FindDataMismatches():

    # Constructor for initializing
    def __init__(self, master_database_cursor, current_database_cursor):
        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def convert_to_yyyymmdd(self, date_str):
        try:
            date_object = datetime.strptime(date_str, "%d-%b-%Y")
            return date_object.strftime("%Y%m%d")
        except ValueError:
            return None  # Handle invalid date strings gracefully

    def tuple_to_list(self, tup):
        #Convert a tuple to a list.
        return list(tup)

    def find_mismatches(self, tables_master, master_yyyymmdd, current_yyyymmdd):
        new_editions = []
        misc_findings = []
        # Iterate through table names in tables_master and find corresponding table in tables_current_temp
        for table_name in tables_master:
            # add the yyyymmdd to match the complete table name
            temp_master_table_name = utils.insert_text(table_name, master_yyyymmdd, pos_to_insert=1)
            temp_current_table_name = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            # Table exists in both databases; compare content
            # note master_data and current_data will be a list of tuples, i.e., [(),(),()...]
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
                # reminder that were dealing with a lists of tuples, i.e., [(),(),()...] so need to convert to tuples to lists so we can convert dates to compare
                if matching_current_row:
                    master_content = self.tuple_to_list(master_row[2:])  # Get the content of columns 2-4 in master_row
                    current_content = self.tuple_to_list(matching_current_row[2:])  # Get the content of columns 2-4 in current_value
                    # The first two elements in the list are:
                    if "RM" in table_name:
                        master_content[0] = self.convert_to_yyyymmdd(master_content[0])
                        current_content[0] = self.convert_to_yyyymmdd(current_content[0])
                    else:
                        # The second and third elements in the list are:
                        master_content[1:3] = [self.convert_to_yyyymmdd(value) for value in master_content[1:3]]
                        current_content[1:3] = [self.convert_to_yyyymmdd(value) for value in current_content[1:3]]
                    # compare the edition information
                    if master_content[:3] != current_content[:3]:
                        # Check each field individually for inequality; ensuring that whatever doesn't match is greater (looking for errors)
                        if any(m != c and c > m for m, c in zip(master_content[:3], current_content[:3])):
                            found_new_edition.append(matching_current_row)
                        if any(m != c and c < m for m, c in zip(master_content[:3], current_content[:3])):
                            misc_finding.append(matching_current_row)
            if found_new_edition:
                new_editions.append((temp_current_table_name, found_new_edition))
            if misc_finding:
                misc_findings.append((temp_master_table_name, misc_finding))
        return new_editions, misc_findings

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
