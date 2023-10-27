'''
Creates the sqlite database and populates tables by reading from CHS DVDs inserted in DVD reader.
Intent is that user will only load one CHS East and one CHS West DVD.
This forms the database. Later code will read current CHS DVDs and compare data to what is in database
to check for errors, new charts, new editions, charts withdrawn and potential errors.

Intent later is to modify this code to also read from a .zip file (this is how the monthly data is received).

'''

import os
import common_utils as utils

class BuildDatabase():

    def __init__(self, master_database_name, rebuild_checkbox, create_database_textbox, database_input_path):
        self.master_database_name = master_database_name
        # Create custom_signals connections
        self.rebuild_checkbox = rebuild_checkbox
        self.create_database_textbox = create_database_textbox

        # database data input path
        self.input_data_path = database_input_path

    def pre_build_checks(self):
        rebuild_selected = True
        path_selected = True

        # delete if necessary; database will be rebuilt
        if os.path.exists(self.master_database_name):
            if not utils.confirm_database_deletion(self.rebuild_checkbox, self.master_database_name, self.create_database_textbox):
                rebuild_selected = False
        
        # ensure user has selected a data input path
        if not utils.confirm_data_path(self.input_data_path):
            path_selected = False
        
        return rebuild_selected, path_selected

    def generate_database(self, master_database_conn, master_database_cursor):
        # declare master database connection and cursor
        self.master_database_conn = master_database_conn
        self.master_database_cursor = master_database_cursor

        if self.input_data_path[:1] == "C": #  Case 1: the files are in a folder on the desktop
            self.process_desktop_folder()
        else:# Case 2: files are on a DVD reader
            self.process_dvd()
        # Commit the changes at the end
        self.master_database_conn.commit()
        self.create_database_textbox.emit("\nCHS Database Successfully Created!")

    def process_dvd(self):
        # default to two DVDs; one East and one West
        num_sources = 2
        for source_num in range(1, num_sources + 1): 
            utils.show_warning_popup(f"Insert DVD {source_num} and press Enter when ready...")
            dvd_name = utils.get_dvd_name(self.input_data_path)
            if dvd_name:
                folders = utils.list_folders(self.input_data_path)
                if folders:
                    self.create_database_textbox.emit(f"\Added '{dvd_name}' to database.")
                    # database data input path is self.input_data_path
                    self.process_folders(folders, self.input_data_path, dvd_name)
                else:
                    self.create_database_textbox.emit(f"\nNo folders found in '{dvd_name}'.")
            else:
                self.create_database_textbox.emit(f"\nDVD not found at path '{self.input_data_path}'.")

    def process_desktop_folder(self):
        # Get the list of foldernames in the subject folder
        foldernames = os.listdir(self.input_data_path)
        # Check if two folders were found
        if len(foldernames) == 2:
            for folder_name in foldernames:
                # build desktop folder path
                desktop_folder_path = os.path.join(self.input_data_path, folder_name)
                folders = utils.list_folders(desktop_folder_path)
                if folders:
                    self.create_database_textbox.emit(f"\nAdded '{desktop_folder_path}' to database.")
                    self.process_folders(folders, desktop_folder_path, folder_name)
                else:
                    self.create_database_textbox.emit(f"\no folders found in '{desktop_folder_path}'.")
        elif len(foldernames) < 2:
            # Inform the user that not enough matching files were found
            print("\nNot enough matching files were found in the folder. Need at least two.")
        else:
            # Inform the user that there are more than two matching files
            print("\nThere are more than two matching files in the folder. Please remove any extras.")

    def process_folders(self, folders, folder_path, source_name):
        for folder in folders:
            if folder.startswith("RM") or folder.startswith("V"):
                self.process_folder(folder, folder_path, source_name)

    def process_folder(self, folder, folder_path, source_name):
        table_name = f"{source_name}_{folder.replace('-', '_')}"
        sub_folder_path = os.path.join(folder_path, folder)
        txt_files = utils.get_txt_files(sub_folder_path)
        if txt_files:
            for txt_file in txt_files:
                txt_file_path = os.path.join(sub_folder_path, txt_file)
                utils.create_table(table_name, txt_file_path, self.master_database_cursor)  # Create the table
                utils.insert_data(table_name, txt_file_path, self.master_database_cursor)    # Insert data into the table
        else:
            self.create_database_textbox.emit("\nNo .txt files in this folder.")
   
if __name__ == "__main__":
   pass
