'''
Creates the sqlite database and populates tables by reading from CHS DVDs inserted in DVD reader.
Intent is that user will only load one CHS East and one CHS West DVD.
This forms the database. Later code will read current CHS DVDs and compare data to what is in database
to check for errors, new charts, new editions, charts withdrawn and potential errors.

Intent later is to modify this code to also read from a .zip file (this is how the monthly data is received).

'''

import sqlite3
import os
import subprocess
from common_utils import show_warning_popup, update_text_browser
from datetime import datetime

class CreateDatabase():

    def __init__(self, database_signals):
        self.database_name = 'chs_dvd.db'
        # Create an instance of CreateDatabaseSignals
        self.database_signals = database_signals

    def delete_existing_database(self, text_browser_widget):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)
            update_text_browser(text_browser_widget, f"Database '{self.database_name}' deleted.")

    def open_database(self, text_browser_widget):
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()
        update_text_browser(text_browser_widget, f"New '{self.database_name}' created and opened")

    def close_database(self, text_browser_widget):
        if self.conn:
            self.conn.close()
        update_text_browser(text_browser_widget, 'close database')

    # Function to get the DVD name using the disk path
    def get_dvd_name(self, input_data_path):
        output = subprocess.check_output(f'wmic logicaldisk where DeviceID="{input_data_path[:2]}" get volumename', text=True)
        lines = output.strip().split('\n')
        dvd_name = lines[2] if len(lines) > 1 else ''
        return dvd_name.strip() if dvd_name else None

    # Function to list folders in the DVD path
    def list_folders(self, dvd_path):
        if os.path.exists(dvd_path):
            folders = [item for item in os.listdir(dvd_path) if os.path.isdir(os.path.join(dvd_path, item))]
            return folders
        else:
            return []

    # Function to create a table with column names from a text file
    def create_table(self, table_name, txt_file_path):
        with open(txt_file_path, 'r') as txt_file:
            column_names = txt_file.readline().strip().split('\t')
            sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
            quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
            column_names_sql = ', '.join(quoted_column_names)
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
            self.cursor.execute(create_table_sql)

    # Function to insert data into a table from a text file
    def insert_data(self, table_name, txt_file_path):
        with open(txt_file_path, 'r') as txt_file:
            next(txt_file)  # Skip the first line (column names)
            next(txt_file)  # Skip the second line
            for line in txt_file:
                line = line.strip()
                if not line:  # Stop processing if the line is blank
                    break
                data = line.split('\t')
                placeholders = ', '.join(['?'] * len(data))
                insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                self.cursor.execute(insert_sql, data)

    # Function to get a list of .txt files in a folder
    def get_txt_files(self, folder_path):
        txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]
        return txt_files
    
    def build_database(self, input_data_path, text_browser_widget):
        self.input_data_path = input_data_path
        # num_sources can be either number of disks or number of files
        self.num_sources = 2

        for source_num in range(1, self.num_sources + 1):
            drive = self.input_data_path[:1]
            if drive == "C":
                # Case 1: If it's a desktop folder (assuming specific filenames)
                dvd_folder_path = os.path.join(self.input_data_path, f"East_West DVD")
                east_filename = f"EastDVD_{datetime.now().strftime('%Y%m')}"
                west_filename = f"WestDVD_{datetime.now().strftime('%Y%m')}"

                if os.path.exists(os.path.join(dvd_folder_path, east_filename)) and os.path.exists(os.path.join(dvd_folder_path, west_filename)):
                    self.process_desktop_folder(dvd_folder_path, text_browser_widget)
                else:
                    update_text_browser(text_browser_widget, f"Required files not found in folder '{dvd_folder_path}'.")
            else:# Case 2: If it's a directory (assuming DVD drive)
                self.process_dvd(text_browser_widget, source_num)

        # Commit the changes at the end
        self.conn.commit()
        update_text_browser(text_browser_widget, "\nCHS Database Successfully Created!")

    def process_dvd(self, source_num, text_browser_widget):

        show_warning_popup(f"Insert DVD {source_num} and press Enter when ready...")
            
        dvd_name = self.get_dvd_name(self.input_data_path)

        if dvd_name:
            folders = self.list_folders(self.input_data_path)

            if folders:
                update_text_browser(text_browser_widget, f"Folders on DVD '{dvd_name}':")
                self.process_folders(folders, text_browser_widget)
            else:
                update_text_browser(text_browser_widget, f"No folders found on DVD '{dvd_name}'.")
        else:
            update_text_browser(text_browser_widget, f"DVD not found at path '{self.input_data_path}'.")

    def process_folders(self, folders, text_browser_widget):
        for folder in folders:
            if folder.startswith("RM") or folder.startswith("V"):
                self.process_folder(folder, text_browser_widget)

    def process_folder(self, folder, text_browser_widget):
        table_name = folder.replace("-", "_")
        folder_path = os.path.join(self.input_data_path, folder)
        txt_files = self.get_txt_files(folder_path)

        if txt_files:
            update_text_browser(text_browser_widget, f"Folder: {folder}")
            for txt_file in txt_files:
                txt_file_path = os.path.join(folder_path, txt_file)
                self.create_table(table_name, txt_file_path)
                self.insert_data(table_name, txt_file_path)
            update_text_browser(text_browser_widget, "Table and data added.")
        else:
            update_text_browser(text_browser_widget, "No .txt files in this folder.")

    def process_desktop_folder(self, folder_path, text_browser_widget):
        east_filename = f"EastDVD_{datetime.now().strftime('%Y%m%d')}"
        west_filename = f"WestDVD_{datetime.now().strftime('%Y%m%d')}"

        east_txt_file = os.path.join(folder_path, east_filename + ".txt")
        west_txt_file = os.path.join(folder_path, west_filename + ".txt")

        if os.path.exists(east_txt_file) and os.path.exists(west_txt_file):
            update_text_browser(text_browser_widget, f"Files found: {east_filename}.txt and {west_filename}.txt")
            # Continue with database construction using the two files...
        else:
            update_text_browser(text_browser_widget, f"Required files not found in folder '{folder_path}'.")
   
if __name__ == "__main__":
    pass
