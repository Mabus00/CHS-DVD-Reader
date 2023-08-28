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
from common_utils import show_warning_popup

class CreateDatabase():

    def __init__(self, database_signals):
        self.database_name = 'chs_dvd.db'
        # Create an instance of CreateDatabaseSignals
        self.database_signals = database_signals

    def __del__(self):
        self.database_signals.progress_reports_textbox.emit('close database')
        # Close the connection after processing all disks
        self.conn.close()  

    def delete_existing_database(self):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)
            self.database_signals.progress_reports_textbox.emit(f"Database '{self.database_name}' deleted.")

    def open_database(self):
        self.database_signals.progress_reports_textbox.emit(f"New '{self.database_name}' created and opened")
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()

    def close_database(self):
        self.database_signals.progress_reports_textbox.emit('close database')
        if self.conn:
            self.conn.close()

    # Function to get the DVD name using the disk path
    def get_dvd_name(self, disk_path):
        output = subprocess.check_output(f'wmic logicaldisk where DeviceID="{disk_path[:2]}" get volumename', text=True)
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
    
    def process_disks(self, disk_path):
        self.disk_path = disk_path
        num_disks = 2

        for disk_num in range(1, num_disks + 1):
            show_warning_popup(f"Insert DVD {disk_num} and press Enter when ready...")
            
            dvd_name = self.get_dvd_name(self.disk_path)

            if dvd_name:
                folders = self.list_folders(self.disk_path)

                if folders:
                    self.database_signals.progress_reports_textbox.emit(f"Folders on DVD '{dvd_name}':")
                    self.process_folders(folders)
                else:
                    self.database_signals.progress_reports_textbox.emit(f"No folders found on DVD '{dvd_name}'.")
            else:
                self.database_signals.progress_reports_textbox.emit(f"DVD not found at path '{self.disk_path}'.")

        # Commit the changes at the end
        self.conn.commit()

    def process_folders(self, folders):
        for folder in folders:
            if folder.startswith("RM") or folder.startswith("V"):
                self.process_folder(folder)

    def process_folder(self, folder):
        table_name = folder.replace("-", "_")
        folder_path = os.path.join(self.disk_path, folder)
        txt_files = self.get_txt_files(folder_path)

        if txt_files:
            self.database_signals.progress_reports_textbox.emit(f"Folder: {folder}")
            for txt_file in txt_files:
                txt_file_path = os.path.join(folder_path, txt_file)
                self.create_table(table_name, txt_file_path)
                self.insert_data(table_name, txt_file_path)
            self.database_signals.progress_reports_textbox.emit("Table and data added.")
        else:
            self.database_signals.progress_reports_textbox.emit("No .txt files in this folder.")
   
if __name__ == "__main__":
    pass
