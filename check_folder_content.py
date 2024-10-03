'''
Checks the folder content of each folder in the current database to the folder's .csv file to confirm the contents are as listed.

e.g., for the RM-ARC folder in the EAST folder, the charts listed in the RM-ARC.csv are in the associated BSBCHART folder

'''

import os
import pandas as pd

# Define the RunChecker class
class CheckFolderContent():

    # Constructor for initializing the CheckFolder object
    def __init__(self, current_database_cursor):
        # Establish database cursors
        self.current_database_cursor = current_database_cursor

    def find_folder(self, starting_directory, target_folder_name):
        # Recursively searches for a folder with a specific name starting from the given directory.
        for root, dirs, files in os.walk(starting_directory):
            for dir_name in dirs:
                if dir_name == target_folder_name:
                    return os.path.join(root, dir_name)

    def complete_paths(self, folders, database_folder, raster_target_folder, vector_target_folder):
        complete_paths = []
        for folder in folders:
            folder_path = os.path.join(database_folder, folder)
            # Get the list of sub-foldernames in the subject folder
            sub_folders = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
            for sub_folder in sub_folders:
                # Check if 'z-' is in the folder name
                if 'Z_' not in sub_folder:
                    sub_folder_path = os.path.join(folder_path, sub_folder)

                    if "RM" in sub_folder_path:
                        temp_path = self.find_folder(sub_folder_path, raster_target_folder)
                    else:
                        temp_path = self.find_folder(sub_folder_path, vector_target_folder)
                
                    complete_paths.append(os.path.dirname(temp_path))
            
        return complete_paths

    def find_and_read_csv(self, base_path):
        # Iterate through the directory structure
        for root, dirs, files in os.walk(base_path):
            # Check if 'RM' is in the directory path
            for file in files:
                # Check if the file is a .csv file
                if file.endswith('.csv'):
                    csv_path = os.path.join(root, file)
                    # Read the CSV file using pandas
                    df = self.read_csv_with_fallback(csv_path)
                    return df
        return None

    def read_csv_with_fallback(self, file_path):
        """Try reading a CSV file with different encodings."""
        encodings = ['utf-8', 'latin1']
        for encoding in encodings:
            try:
                # note here I'm only reading the second column
                return pd.read_csv(file_path, encoding=encoding, skiprows=1, header=None)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not read the file {file_path} with available encodings.")

    def convert_path_to_name(self, path):
        # Split the path into components
        components = path.split('\\')  # Split by backslash for Windows paths

        # Extract the relevant components
        parent_folder = components[-2]  # Second to last component
        last_folder = components[-1]  # Last component

        # Replace dashes and backslashes with underscores in the last folder name
        last_folder_cleaned = last_folder.replace('-', '_').replace('\\', '_')

        # Construct the final name
        final_name = f"{parent_folder}_{last_folder_cleaned}"
        
        return final_name

    def check_folders(self, database_folder, raster_target_folder, vector_target_folder):
        missing_files = []
        extra_files = []

        self.current_database_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_current = [row[0] for row in self.current_database_cursor.fetchall()]

        # Get the list of foldernames in the subject folder
        folders = [item for item in os.listdir(database_folder) if os.path.isdir(os.path.join(database_folder, item))]

        complete_paths = self.complete_paths(folders, database_folder, raster_target_folder, vector_target_folder)

        for path in complete_paths:
            # Find and read the CSV file
            df = self.find_and_read_csv(path)
            formatted_name = self.convert_path_to_name(path) # Output: EastDVD_20240726_RM_ARC
            
            if "RM" in path:
                table_files = self.current_database_cursor.execute(f"SELECT File FROM {formatted_name}")  # Assuming col2 is the column to fetch
                expected_files = df.iloc[:, 1].tolist()
            else:
                table_files = self.current_database_cursor.execute(f"SELECT CELL_NAME FROM {formatted_name}")  # Assuming col2 is the column to fetch
                # Filter out entries in expected_files based on col1 containing "test"
                expected_files = df[df[0].str.contains('Cancel_Annuler') == False][1].tolist()

            table_files = self.current_database_cursor.fetchall()  # Fetch all rows
            table_files = [row[0] for row in table_files]  # Extract values from rows
            
            try:
                # read the extracted second column of the CSV file to extract the list of expected_files
                if not set(expected_files).issubset(set(table_files)):
                    missing_files.append(set(expected_files) - set(formatted_name))
                    extra_files.append(set(formatted_name) - set(expected_files))
            except ValueError as e:
                    print(f"Error reading CSV file {path}: {e}")

        return missing_files, extra_files
    
# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass