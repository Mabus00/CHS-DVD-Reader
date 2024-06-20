'''
Creates the sqlite database and populates tables by reading from CHS DVDs / system files.
If DVDs, intent is that user will only load one CHS East and one CHS West DVD.
This forms the database. Later code will read current CHS DVDs and compare data to what is in database
to check for errors, new charts, new editions, charts withdrawn and potential errors.

'''

import os
import common_utils as utils
import subprocess
import time
import csv

class BuildDatabase():

    def __init__(self, master_database_path, rebuild_checkbox, create_database_textbox, master_database_folder):
        self.master_database_path = master_database_path  # actual path to master database
        # Create custom_signals connections
        self.rebuild_checkbox = rebuild_checkbox
        self.create_database_textbox = create_database_textbox

        # database data input path
        self.master_database_folder = master_database_folder  # path to master database folder

        # target folders to find to process data
        self.raster_target_folder = 'BSBCHART'
        self.vector_target_folder = 'ENCROOT'

    def pre_build_checks(self):
        rebuild_selected = True
        path_selected = True

        # delete if necessary; database will be rebuilt
        if os.path.exists(self.master_database_path):
            if not utils.confirm_database_deletion(self.rebuild_checkbox, self.master_database_path, self.create_database_textbox):
                rebuild_selected = False
        
        # ensure user has selected a data input path
        if not utils.confirm_data_path(self.master_database_folder):
            path_selected = False
        
        return rebuild_selected, path_selected

    def generate_database(self, master_database_conn, master_database_cursor):
        # declare master database connection and cursor
        self.master_database_conn = master_database_conn
        self.master_database_cursor = master_database_cursor

        if self.master_database_folder[:1] == "C": #  Case 1: the files are in a folder on the desktop
            self.process_desktop_folder()
        else:# Case 2: files are on a DVD reader
            self.process_dvd()
        # Commit the changes at the end
        self.master_database_conn.commit()
        self.create_database_textbox.emit(f"\n{self.master_database_path} successfully created!")

    # Function to list folders in the DVD path
    def list_folders(self, folder_path):
        if os.path.exists(folder_path):
            folders = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
            return folders
        else:
            return []

    # Function to get a list of .txt or .csv files in a folder
    def get_files(self, folder_path, file_extension):
        files = [file for file in os.listdir(folder_path) if file.endswith(f".{file_extension}")]
        return files

    # Function to get the DVD name using the disk path; retries introduced because USB connected DVD readers can lag
    def get_dvd_name(self, input_data_path, max_retries=5, retry_interval=1):
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Attempt to retrieve DVD name
                output = subprocess.check_output(f'wmic logicaldisk where DeviceID="{input_data_path[:2]}" get volumename', text=True)
                lines = output.strip().split('\n')
                dvd_name = lines[2] if len(lines) > 1 else ''
                if dvd_name:
                    print(f'Number of retries = {retry_count}') #number of retries
                    dvd_name = dvd_name.replace('EAST', 'East').replace('WEST', 'West')
                    return dvd_name.strip()
            except subprocess.CalledProcessError as e:
                # Handle the error if the subprocess call fails
                print(f"Error while getting DVD name (Attempt {retry_count + 1}): {e}")
            except Exception as e:
                # Handle other exceptions, if any
                print(f"An unexpected error occurred (Attempt {retry_count + 1}): {e}") 
            # Wait for a specified interval before retrying
            time.sleep(retry_interval)
            retry_count += 1
        # Return None if the maximum number of retries is reached
        print("Maximum number of retries reached. DVD name not found.")
        return None

    # Function to create a table with column names from a .txt or .csv file
    def create_table(self, table_name, file_path, cursor, file_extension):
        if file_extension == 'txt':
            with open(file_path, 'r', errors='ignore') as txt_file:
                column_names = txt_file.readline().strip().split('\t')
        else:
            # Detect the encoding of the file
            detected_encoding = utils.detect_encoding(file_path)
            #print(f'create_table detected encoding = {detected_encoding}')
            try:
                # Open the file using the detected encoding
                with open(file_path, 'r', newline='', encoding=detected_encoding) as csv_file:
                    csv_reader = csv.reader(csv_file)
                    # Read the first row to get column names
                    column_names = next(csv_reader)
                    sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
                    quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
                    column_names_sql = ', '.join(quoted_column_names)
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
                    cursor.execute(create_table_sql)
            except UnicodeDecodeError as e:
                print(f"Error in create_table decoding file '{file_path}': {e}")
                # Handle the error as needed

    def process_dvd(self):
        # default to two DVDs; one East and one West
        num_sources = 2
        for source_num in range(1, num_sources + 1): 
            utils.show_warning_popup(f"Insert DVD {source_num} and press Enter when ready...")
            dvd_name = self.get_dvd_name(self.master_database_folder)
            if dvd_name:
                folders = utils.list_folders(self.master_database_folder)
                if folders:
                    self.create_database_textbox.emit(f"\nAdded '{dvd_name}' to the {self.master_database_path}.")
                    # database data input path is self.input_data_path
                    self.process_folders(folders, self.master_database_folder, dvd_name)
                else:
                    self.create_database_textbox.emit(f"\nNo folders found in '{dvd_name}'.")
            else:
                self.create_database_textbox.emit(f"\nDVD not found at path '{self.master_database_folder}'.")

    def process_desktop_folder(self):
        # Get the list of foldernames in the subject folder
        folders = [item for item in os.listdir(self.master_database_folder) if os.path.isdir(os.path.join(self.master_database_folder, item))]
        # Check if two folders were found
        if len(folders) == 2:
            for folder_name in folders:
                # build desktop folder path
                desktop_folder_path = os.path.join(self.master_database_folder, folder_name)
                folders = self.list_folders(desktop_folder_path)
                if folders:
                    self.create_database_textbox.emit(f"\nAdded '{desktop_folder_path}' to the {self.master_database_path}.")
                    self.process_folders(folders, desktop_folder_path, folder_name)
                else:
                    self.create_database_textbox.emit(f"\no folders found in '{desktop_folder_path}'.")
        elif len(folders) < 2:
            # Inform the user that not enough matching files were found
            print("\nNot enough matching files were found in the folder. Need at least two.")
        else:
            # Inform the user that there are more than two matching files
            print("\nThere are more than two matching files in the folder. Please remove any extras.")


    def find_folder(self, starting_directory, target_folder_name):
        """
        Recursively searches for a folder with a specific name starting from the given directory.

        :param starting_directory: The directory from which to start the search.
        :param target_folder_name: The name of the folder to search for.
        :return: The path to the target folder if found, otherwise None.
        """
        for root, dirs, files in os.walk(starting_directory):
            for dir_name in dirs:
                if dir_name == target_folder_name:
                    return os.path.join(root, dir_name)
        return None

    def process_folders(self, folders, folder_path, source_name):
        for folder in folders:
            if folder.startswith("RM") or folder.startswith("V"):
                table_name = f"{source_name}_{folder.replace('-', '_')}"
                sub_folder_path = os.path.join(folder_path, folder)

                if folder.startswith("RM"):
                    complete_path = self.find_folder(sub_folder_path,  self.raster_target_folder)
                else:
                    complete_path = self.find_folder(sub_folder_path,  self.vector_target_folder)
                
                complete_path = os.path.dirname(complete_path)

                for file_name in os.listdir(sub_folder_path):
                    file_path = os.path.join(complete_path, file_name)
                    # following ignores anything that isn't a file (i.e., folders)
                    if os.path.isfile(file_path):
                        # get the extension so file can be read correctly
                        file_extension = file_name.split('.')[-1].lower()
                        files = self.get_files(complete_path, file_extension)
                        if file_extension == "csv" or file_extension == "txt":
                            # it's understood there's only one file; method is written so it can apply if there are >1 files
                            for file in files:
                                file_path = os.path.join(complete_path, file)
                                self.create_table(table_name, file_path, self.master_database_cursor, file_extension)  # Create the table
                                utils.insert_data(table_name, file_path, self.master_database_cursor, file_extension)    # Insert data into the table
                        elif file_extension == "":
                            self.create_database_textbox.emit("\nNo .txt or .csv files in this folder.")
   
if __name__ == "__main__":
   pass
