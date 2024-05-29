'''
Checks the folder content of each folder in the current database to the folder's .csv file to confirm the contents are as listed.

e.g., for the RM-ARC folder in the EAST folder, the charts listed in the RM-ARC.csv are in the associated BSBCHART folder

'''

import os
import pandas as pd

# Define the RunChecker class
class CheckFolderContent():

    # Constructor for initializing the CheckFolder object
    def __init__(self, master_database_cursor, current_database_cursor):
        # Establish database cursors
        self.master_database_cursor = master_database_cursor
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

    def check_folders(self, base_folder):
            # start at base_folder
            for sub_folder in os.listdir(base_folder):
                if any(sub_folder.startswith(prefix) for prefix in self.East_West):
                    sub_folder_path = os.path.join(base_folder, sub_folder)
                    # now in EastDVD or WestDVD folder
                    for sub_sub_folder in os.listdir(sub_folder_path):
                        if any(sub_sub_folder.startswith(prefix) for prefix in self.RM_V):
                            # now in an R- or V- folder
                            sub_sub_folder_path = os.path.join(sub_folder_path, sub_sub_folder)
                            # Find the CSV file and the BSB or ENC folder in the sub-sub-folder
                            csv_file = None
                            sub_sub_sub_folder = None
                            for item in os.listdir(sub_sub_folder_path):
                                if item.endswith('.csv'):
                                    csv_file = os.path.join(sub_sub_folder_path, item)
                                elif any(item.startswith(prefix) for prefix in self.BSB_ENC):
                                    sub_sub_sub_folder = os.path.join(sub_sub_folder_path, item)

                            if csv_file and sub_sub_sub_folder:
                                # Read the second column from the CSV file
                                try:
                                    # read the extracted second column of the CSV file to extract the list of expected_files
                                    df = self.read_csv_with_fallback(csv_file)
                                    expected_files = df.iloc[:, 0].tolist()
                                    
                                    if "BSB" in sub_sub_sub_folder:
                                        # Get the list of actual files in the sub-sub-sub-folder
                                        content = [file for file in os.listdir(sub_sub_sub_folder) if file.endswith('.BSB')]
                                    else:
                                        # List of all directories within sub_sub_sub_folder
                                        content = [item for item in os.listdir(sub_sub_sub_folder) if os.path.isdir(os.path.join(sub_sub_sub_folder, item))]

                                    # Check for missing and extra files
                                    missing_files = [file for file in expected_files if file not in content]
                                    extra_files = [file for file in content if file not in expected_files]
                                    
                                    if missing_files:
                                        print(f"Missing files in {sub_sub_sub_folder}: {missing_files}")
                                    if extra_files:
                                        print(f"Extra files in {sub_sub_sub_folder}: {extra_files}")
                                except ValueError as e:
                                    print(f"Error reading CSV file {csv_file}: {e}")

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass