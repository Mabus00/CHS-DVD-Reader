'''
Binary File Checker
'''

import filecmp
import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import time

# Function to select folder paths
def select_folder():
    folder_selected = filedialog.askdirectory()
    return folder_selected

# Function to split a path into multiple columns
def split_path_to_columns(path):
    return path.split(os.sep)  # Split by directory separator

# Function to export the comparison results to a CSV file
def export_to_csv(file_name, data, runtime, execution_time):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write runtime and execution time at the top of the CSV file
        writer.writerow(["Comparison Run Time", runtime])
        writer.writerow(["Total Execution Time (seconds)", f"{execution_time:.2f}"])
        writer.writerow([])  # Empty row for separation
        
        # Write only differing, funny files, and files in the second directory only
        writer.writerow(["Category", "Path Components"])
        for category, items in data.items():
            if items:
                writer.writerow([category])
                for item in items:
                    if isinstance(item, tuple):  # For differing file pairs or CSV file pairs
                        writer.writerow([item[0], item[1]])
                    else:
                        path_columns = split_path_to_columns(item)
                        writer.writerow([""] + path_columns)
            else:
                writer.writerow([category, "None"])

# Function to compare file contents (using filecmp.cmp with shallow=False)
def compare_file_contents(file1, file2):
    return filecmp.cmp(file1, file2, shallow=False)  # Ensure full file content comparison

# Recursive function to compare directories and subdirectories (except CSV files)
def compare_directories_recursive(comparison, comparison_data, dir1, dir2):
    # Compare files in the directory by checking contents using filecmp.cmp(shallow=False)
    for file in comparison.common_files:
        file1 = os.path.join(comparison.left, file)
        file2 = os.path.join(comparison.right, file)
        # Skip .csv files, .031, and .TXT files, as we compare them only in dir2
        if not file1.endswith((".csv", ".031", ".TXT")) and not compare_file_contents(file1, file2):
            comparison_data["Differing files"].append(file1)

    for file in comparison.funny_files:
        comparison_data["Files that cannot be compared"].append(os.path.join(comparison.left, file))

    # We will only track files that are in the second directory and not in the first
    for file in comparison.right_only:
        comparison_data["Only in second directory"].append(os.path.join(comparison.right, file))

    # Recursively compare subdirectories
    for subdir_name, subdir_cmp in comparison.subdirs.items():
        compare_directories_recursive(subdir_cmp, comparison_data, dir1, dir2)

# Function to map and compare specific folders like EastDVD and WestDVD (for non-CSV files)
def map_and_compare_folders(dir1, dir2, comparison_data):
    # Find corresponding folders (EastDVD and WestDVD)
    for root1, dirs1, files1 in os.walk(dir1):
        for dir_name in dirs1:
            if dir_name.startswith("EastDVD"):
                # Match the corresponding EastDVD folder in dir2
                match_dir2 = find_matching_folder(dir2, "EastDVD")
                if match_dir2:
                    comparison = filecmp.dircmp(os.path.join(root1, dir_name), match_dir2)
                    compare_directories_recursive(comparison, comparison_data, os.path.join(root1, dir_name), match_dir2)

            elif dir_name.startswith("WestDVD"):
                # Match the corresponding WestDVD folder in dir2
                match_dir2 = find_matching_folder(dir2, "WestDVD")
                if match_dir2:
                    comparison = filecmp.dircmp(os.path.join(root1, dir_name), match_dir2)
                    compare_directories_recursive(comparison, comparison_data, os.path.join(root1, dir_name), match_dir2)

# Function to find the matching EastDVD or WestDVD folder in the second directory
def find_matching_folder(base_dir, prefix):
    for root, dirs, _ in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name.startswith(prefix):
                return os.path.join(root, dir_name)
    return None

# Function to compare all CSV files within the second directory that contain 'CHS_COLLECTIONS_ENCS57'
def compare_csv_files_in_directory(dir2, comparison_data):
    csv_files = []

    # Walk through the directory and find all .csv files containing 'CHS_COLLECTIONS_ENCS57'
    for root, _, files in os.walk(dir2):
        for file in files:
            if file.endswith(".csv") and "CHS_COLLECTIONS_ENCS57" in file:
                csv_files.append(os.path.join(root, file))

    # Compare each pair of .csv files
    for i in range(len(csv_files)):
        for j in range(i + 1, len(csv_files)):
            file1 = csv_files[i]
            file2 = csv_files[j]

            # Compare the two .csv files using filecmp.cmp with shallow=False to compare content
            if not compare_file_contents(file1, file2):  # Only track differing .csv files
                comparison_data["Differing CSV files"].append((file1, file2))

# Function to compare files in the second directory that have the same name and extension
def compare_files_with_same_name_and_extension(dir2, comparison_data):
    files_by_name_and_extension = {}

    # Walk through the directory and group files by name and extension
    for root, _, files in os.walk(dir2):
        for file in files:
            # Skip .031 and .TXT files
            if file.endswith((".031", ".TXT")):
                continue
            name_ext = os.path.splitext(file)  # (name, extension)
            if name_ext not in files_by_name_and_extension:
                files_by_name_and_extension[name_ext] = []
            files_by_name_and_extension[name_ext].append(os.path.join(root, file))

    # Compare files with the same name and extension
    for name_ext, file_paths in files_by_name_and_extension.items():
        if len(file_paths) > 1:
            # Compare each pair of files with the same name and extension
            for i in range(len(file_paths)):
                for j in range(i + 1, len(file_paths)):
                    file1 = file_paths[i]
                    file2 = file_paths[j]
                    if not compare_file_contents(file1, file2):  # Only track differing files
                        comparison_data["Differing files with same name and extension"].append((file1, file2))

# Function to compare two directories and their subdirectories
def compare_directories(dir1, dir2):
    if not os.path.exists(dir1) or not os.path.exists(dir2):
        messagebox.showerror("Error", "One or both directories do not exist")
        return

    # Capture the current time and start the timer
    runtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()

    # Initialize an empty dictionary to store the comparison results
    comparison_data = {
        "Differing files": [],
        "Files that cannot be compared": [],
        "Only in second directory": [],
        "Differing CSV files": [],
        "Differing files with same name and extension": []
    }

    # Map and compare the specific folders (EastDVD and WestDVD)
    map_and_compare_folders(dir1, dir2, comparison_data)

    # Compare all .csv files within the second directory that contain 'CHS_COLLECTIONS_ENCS57'
    compare_csv_files_in_directory(dir2, comparison_data)

    # Compare files in the second directory that have the same name and extension (excluding .031 and .TXT)
    compare_files_with_same_name_and_extension(dir2, comparison_data)

    # Stop the timer and calculate the execution time
    end_time = time.time()
    execution_time = end_time - start_time

    # Ask the user where to save the CSV file
    csv_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    if csv_file_path:
        export_to_csv(csv_file_path, comparison_data, runtime, execution_time)
        messagebox.showinfo("Export Complete", f"Comparison results saved to {csv_file_path}\nTotal execution time: {execution_time:.2f} seconds")

# Function to start the comparison
def start_comparison():
    dir1 = select_folder()
    if not dir1:
        messagebox.showerror("Error", "No first folder selected")
        return
    
    dir2 = select_folder()
    if not dir2:
        messagebox.showerror("Error", "No second folder selected")
        return
    
    compare_directories(dir1, dir2)

# Create main window
root = tk.Tk()
root.title("Folder Comparison Tool")

# Add a button to start the folder comparison
compare_button = tk.Button(root, text="Select Folders and Compare", command=start_comparison)
compare_button.pack(pady=20)

# Start the tkinter main loop
root.mainloop()
