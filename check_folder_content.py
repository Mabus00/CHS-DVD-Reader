'''
Checks the folder content of each folder in the current database to the folder's .csv file to confirm the contents are as listed.

e.g., for the RM-ARC folder in the EAST folder, the charts listed in the RM-ARC.csv are in the associated BSBCHART folder

'''

import common_utils as utils

# Define the RunChecker class
class CheckFolderContent():

    # Constructor for initializing the CheckFolder object
    def __init__(self, master_database_cursor, current_database_cursor):
        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def check_folders(self, current_database_path):
        charts_missing = []
        # Get the list of table names for current_database
        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # extract all the table names from the current_database
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]
        # divide into east and west table and only keep the parts that march the folder names; lists will be used to scan sub-folders
        east_tables = ["-".join(table.split("_")[2:]) for table in tables_current if table.startswith("EastDVD_")]
        west_tables = ["-".join(table.split("_")[2:]) for table in tables_current if table.startswith("WestDVD_")]
        '''
        best approach - create tables with entries and compare the tables.
        
        best way might be to create tables of folder contents of each folder then compare that to the entries in the table.

        EastDVD, folder name (e.g., RM-ARC), sub-folder name (e.g., BSBCHART), create list of contents.
        Compare that to below; is file name in the above folder?

        '''
        for table in tables_current:
            if "RM" in table:
                self.current_database_cursor.execute(f"SELECT File FROM {table};")
                files = self.current_database_cursor.fetchall()
                print(f"Contents of File column in table {table}:")
                for file_row in files:
                    print(file_row[0])
            else:
                self.current_database_cursor.execute(f"SELECT CELL_NAME FROM {table};")
                files = self.current_database_cursor.fetchall()
                print(f"Contents of CELL_NAME column in table {table}:")
                for file_row in files:
                    print(file_row[0])

        return charts_missing

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass