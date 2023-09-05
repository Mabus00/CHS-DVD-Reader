'''
Creates the sqlite database and populates tables by reading from CHS DVDs inserted in DVD reader.
Intent is that user will only load one CHS East and one CHS West DVD.
This forms the database. Later code will read current CHS DVDs and compare data to what is in database
to check for errors, new charts, new editions, charts withdrawn and potential errors.

Intent later is to modify this code to also read from a .zip file (this is how the monthly data is received).

'''

import os
import common_utils as utils
from datetime import datetime

class CreateDatabase():

    def __init__(self, database_signals, create_database_conn, create_database_cursor):
        # Create an instance of CreateDatabaseSignals
        self.database_signals = database_signals
        self.create_database_conn = create_database_conn
        self.create_database_cursor = create_database_cursor
    
    def generate_database(self, input_data_path, text_browser_widget):
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
                    utils.update_text_browser(text_browser_widget, f"Required files not found in folder '{dvd_folder_path}'.")
            else:# Case 2: If it's a directory (assuming DVD drive)
                self.process_dvd(source_num, text_browser_widget)

        # Commit the changes at the end
        self.create_database_conn.commit()
        utils.update_text_browser(text_browser_widget, "\nCHS Database Successfully Created!")

    def process_dvd(self, source_num, text_browser_widget):

        utils.show_warning_popup(f"Insert DVD {source_num} and press Enter when ready...")
            
        dvd_name = utils.get_dvd_name(self.input_data_path)

        if dvd_name:
            folders = utils.list_folders(self.input_data_path)

            if folders:
                utils.update_text_browser(text_browser_widget, f"Folders on DVD '{dvd_name}':")
                self.process_folders(folders, text_browser_widget, dvd_name)
            else:
                utils.update_text_browser(text_browser_widget, f"No folders found on DVD '{dvd_name}'.")
        else:
            utils.update_text_browser(text_browser_widget, f"DVD not found at path '{self.input_data_path}'.")

    def process_folders(self, folders, text_browser_widget, dvd_name):
        for folder in folders:
            if folder.startswith("RM") or folder.startswith("V"):
                self.process_folder(folder, text_browser_widget, dvd_name)

    def process_folder(self, folder, text_browser_widget, dvd_name):
        table_name = f"{dvd_name}_{folder.replace('-', '_')}"
        folder_path = os.path.join(self.input_data_path, folder)
        txt_files = utils.get_txt_files(folder_path)

        if txt_files:
            utils.update_text_browser(text_browser_widget, f"Folder: {folder}")
            for txt_file in txt_files:
                txt_file_path = os.path.join(folder_path, txt_file)
                utils.create_table(table_name, txt_file_path, self.create_database_cursor)  # Create the table
                utils.insert_data(table_name, txt_file_path, self.create_database_cursor)    # Insert data into the table
            utils.update_text_browser(text_browser_widget, "Table and data added.")
        else:
            utils.update_text_browser(text_browser_widget, "No .txt files in this folder.")

    def process_desktop_folder(self, folder_path, text_browser_widget):
        east_filename = f"EastDVD_{datetime.now().strftime('%Y%m%d')}"
        west_filename = f"WestDVD_{datetime.now().strftime('%Y%m%d')}"

        east_txt_file = os.path.join(folder_path, east_filename + ".txt")
        west_txt_file = os.path.join(folder_path, west_filename + ".txt")

        if os.path.exists(east_txt_file) and os.path.exists(west_txt_file):
            utils.update_text_browser(text_browser_widget, f"Files found: {east_filename}.txt and {west_filename}.txt")
            # Continue with database construction using the two files...
        else:
            utils.update_text_browser(text_browser_widget, f"Required files not found in folder '{folder_path}'.")
   
if __name__ == "__main__":
    pass
