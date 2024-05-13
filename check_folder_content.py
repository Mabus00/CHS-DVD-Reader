'''
Checks the folder content of each folder in the current database to the folder's .csv file to confirm the contents are as listed.

e.g., for the RM-ARC folder in the EAST folder, the charts listed in the RM-ARC.csv are in the associated BSBCHART folder

'''

import common_utils as utils
import os
import csv

# Define the RunChecker class
class CheckFolderContent():

    # Constructor for initializing the CheckFolder object
    def __init__(self, master_database_cursor, current_database_cursor):
        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def compare_csv_to_files(self, csv_path, bsbchart_path):
        # Read CSV file
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            # Skip header if present
            next(csv_reader)
            # Extract second column
            csv_data = [row[1] for row in csv_reader]

        # Get list of files in BSBCHART folder
        bsbchart_files = os.listdir(bsbchart_path)

        # Compare CSV data to BSBCHART files
        for filename in bsbchart_files:
            if filename in csv_data:
                print(f"{filename} found in CSV")
            else:
                print(f"{filename} not found in CSV")
        
    def check_folders(self, current_database_folder):
        charts_missing = []

        for root, dirs, files in os.walk(current_database_folder):
            for dir_name in dirs:
                # Extract part before underscore
                dvd_folder_name = dir_name.split('_')[0]
                if dvd_folder_name.startswith('EastDVD') or dvd_folder_name.startswith('WestDVD'):
                    dvd_path = os.path.join(root, dir_name)
                    for root, dirs, files in os.walk(dvd_path):
                        for file in files:
                            if file.endswith('.csv'):
                                csv_path = os.path.join(root, file)
                                bsbchart_path = os.path.join(root, 'BSBCHART')
                                self.compare_csv_to_files(csv_path, bsbchart_path)

        return charts_missing

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass