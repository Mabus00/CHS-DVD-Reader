'''
Checks the folder content of each folder in the current database to the folder's .csv file to confirm the contents are as listed.

e.g., for the RM-ARC folder in the EAST folder, the charts listed in the RM-ARC.csv are in the associated BSBCHART folder

'''

import os
import pandas as pd

import common_utils as utils

# Define the RunChecker class
class CheckFolderContent():

    # Constructor for initializing the CheckFolder object
    def __init__(self, current_database_cursor):
        # Establish database cursors
        self.current_database_cursor = current_database_cursor

        self.East_West = ['EastDVD_', 'WestDVD_']
        self.RM_V = ['RM-', 'V-']
        self.BSB_ENC = ['BSBCHART', 'ENC_ROOT']

    def read_csv_with_fallback(self, file_path):
        """Try reading a CSV file with different encodings."""
        encodings = ['utf-8', 'latin1']
        for encoding in encodings:
            try:
                # note here I'm only reading the second column
                return pd.read_csv(file_path, usecols=[1], encoding=encoding, skiprows=1, header=None)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not read the file {file_path} with available encodings.")

    def check_folders(self, database_folder, raster_target_folder, vector_target_folder):
        missing_files = []
        extra_files = []

        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]

        # Get the list of foldernames in the subject folder
        folders = [item for item in os.listdir(database_folder) if os.path.isdir(os.path.join(database_folder, item))]

        for folder in folders:
            # Get the list of sub-foldernames in the subject folder
            sub_folders = [item for item in os.listdir(folder) if os.path.isdir(os.path.join(folder, item))]

            for sub_folders in folder:

                if sub_folders.startswith("RM"):
                    complete_path = utils.find_folder(sub_folders, raster_target_folder)
                else:
                    complete_path = utils.find_folder(sub_folders, vector_target_folder)
                
                complete_path = os.path.dirname(complete_path)

                for item in os.listdir(complete_path):
                    if item.endswith('.csv'):
                        csv_file = os.path.join(complete_path, item)

                        try:
                            # read the extracted second column of the CSV file to extract the list of expected_files
                            df = self.read_csv_with_fallback(csv_file)
                            expected_files = df.iloc[:, 0].tolist()

                            print('here')

                            # # Check for missing and extra files
                            # missing = [file for file in expected_files if file not in content]
                            # extra = [file for file in content if file not in expected_files]
                            
                            # if missing:
                            #     missing_files.append(f"Missing files in {sub_sub_folder}: {missing}")
                            # if extra:
                            #     extra_files.appen(f"Extra files in {sub_sub_folder}: {extra}")
                        except ValueError as e:
                            print(f"Error reading CSV file {csv_file}: {e}")

        return missing_files, extra_files
    
# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass