'''
To call this function
from Binary_File_Checker import FolderComparison
comparison = FolderComparison(master_database_path, current_database_path)
'''
import filecmp
import os
import csv
from datetime import datetime
import time

import common_utils as utils
from PyQt5.QtCore import QCoreApplication

class BinaryFileChecker:
    def __init__(self, ui, main_page_textbox):
        super().__init__()  # call __init__ of the parent class chs_dvd_reader_main

        self.ui = ui
        # Create custom_signals connections
        self.main_page_textbox = main_page_textbox

        self.master_database_path = ''
        self.current_database_path = ''

        self.comparison_data = {
            "New Editions": [],  # Files that have changed from the last CD to current. Watch for files that don't have new editions released
            "Files that cannot be compared": [],  # files
            "Updates and New Charts": [],  # Only on the second CD
            "Withdrawn": [],  # Only on the first CD
            "Differing files with same name and extension": []  # Checks for ENCs in multiple collections to see if they all receive the new edition.
        }
        self.runtime = None
        self.execution_time = None

    # Function to split a path into multiple columns
    def split_path_to_columns(self, path):
        return path.split(os.sep)

    # Function to get only the final part of a file or folder path
    def get_end_of_path(self, path):
        return os.path.basename(path)

    # Function to export the comparison results to a CSV file
    def export_to_csv(self):
        # Define the CSV path inside current_database_path folder with the name bit_checker_results.csv
        csv_file_path = os.path.join(self.current_database_path, "bit_checker_results.csv")
        
        # Write to the CSV file, overwriting if it exists
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Comparison Run Time", self.runtime])
            writer.writerow(["Total Execution Time (seconds)", f"{self.execution_time:.2f}"])
            writer.writerow([])  # Empty row for separation

            writer.writerow(["Category", "Path Components"])
            for category, items in self.comparison_data.items():
                if items:
                    writer.writerow([category])
                    for item in items:
                        if isinstance(item, tuple):  # For differing file pairs
                            writer.writerow([item[0], item[1]])
                        else:
                            path_columns = self.split_path_to_columns(item)
                            writer.writerow([""] + path_columns)
                else:
                    writer.writerow([category, "None"])

    # Function to compare file contents (using filecmp.cmp with shallow=False)
    def compare_file_contents(self, file1, file2):
        return filecmp.cmp(file1, file2, shallow=False)

    # Recursive function to compare directories and subdirectories
    def compare_directories_recursive(self, comparison):
        # Compare files in both directories
        for file in comparison.common_files:
            file1 = os.path.join(comparison.left, file)
            file2 = os.path.join(comparison.right, file)
            if not file1.endswith((".csv", ".031", ".TXT")) and not self.compare_file_contents(file1, file2):
                self.comparison_data["New Editions"].append(file1)

        # Files that cannot be compared
        for file in comparison.funny_files:
            self.comparison_data["Files that cannot be compared"].append(os.path.join(comparison.left, file))

        # Files only in the second directory (excluding .csv files)
        for file in comparison.right_only:
            if not file.endswith(".csv"):  # Exclude .csv files
                self.comparison_data["Updates and New Charts"].append(os.path.join(comparison.right, file))

        # Files only in the first directory (excluding .csv files)
        for file in comparison.left_only:
            if not file.endswith(".csv"):  # Exclude .csv files
                self.comparison_data["Withdrawn"].append(os.path.join(comparison.left, file))

        # Recursively compare subdirectories
        for subdir_name, subdir_cmp in comparison.subdirs.items():
            self.compare_directories_recursive(subdir_cmp)

    # Function to map and compare specific folders like EastDVD and WestDVD
    def map_and_compare_folders(self):
        for root1, dirs1, _ in os.walk(self.master_database_path):
            for dir_name in dirs1:
                if dir_name.startswith("EastDVD"):
                    match_current_database_path = self.find_matching_folder(self.current_database_path, "EastDVD")  
                    if match_current_database_path:
                        comparison = filecmp.dircmp(os.path.join(root1, dir_name), match_current_database_path)
                        self.compare_directories_recursive(comparison)
                elif dir_name.startswith("WestDVD"):
                    match_current_database_path = self.find_matching_folder(self.current_database_path, "WestDVD")
                    if match_current_database_path:
                        comparison = filecmp.dircmp(os.path.join(root1, dir_name), match_current_database_path)
                        self.compare_directories_recursive(comparison)

    # Function to find the matching EastDVD or WestDVD folder in the second directory
    def find_matching_folder(self, base_dir, prefix):
        for root, dirs, _ in os.walk(base_dir):
            for dir_name in dirs:
                if dir_name.startswith(prefix):
                    return os.path.join(root, dir_name)
        return None

    # Function to compare files in the second directory that have the same name and extension
    def compare_files_with_same_name_and_extension(self):
        files_by_name_and_extension = {}
        for root, _, files in os.walk(self.current_database_path):
            for file in files:
                if file.endswith((".031", ".TXT")):
                    continue
                name_ext = os.path.splitext(file)
                if name_ext not in files_by_name_and_extension:
                    files_by_name_and_extension[name_ext] = []
                files_by_name_and_extension[name_ext].append(os.path.join(root, file))

        for file_paths in files_by_name_and_extension.values():
            if len(file_paths) > 1:
                for i in range(len(file_paths)):
                    for j in range(i + 1, len(file_paths)):
                        file1 = file_paths[i]
                        file2 = file_paths[j]
                        if not self.compare_file_contents(file1, file2):
                            self.comparison_data["Differing files with same name and extension"].append((file1, file2))

    # Function to start the comparison process
    def compare_directories(self, master_database_path, current_database_path):
        self.main_page_textbox.emit(f"\nStarting bit checker process.")
        QCoreApplication.processEvents()  # forces the textbox to update with message

        self.master_database_path = master_database_path
        self.current_database_path = current_database_path

        self.runtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()

        self.main_page_textbox.emit(f"\nComparing folders.")
        QCoreApplication.processEvents()  # forces the textbox to update with message
        self.map_and_compare_folders()

        self.main_page_textbox.emit(f"\nComparing files.")
        QCoreApplication.processEvents()  # forces the textbox to update with message
        self.compare_files_with_same_name_and_extension()

        end_time = time.time()
        self.execution_time = end_time - start_time

        self.main_page_textbox.emit(f"\nExporting results.")
        QCoreApplication.processEvents()  # forces the textbox to update with message
        self.export_to_csv()



if __name__ == "__main__":
    pass
