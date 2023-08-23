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

class CreateDatabase():

    def __init__(self, database_name):
        self.database_name = database_name

    def __del__(self):
        # Close the connection after processing all disks
        self.conn.close()

    def delete_existing_database(self):
        if os.path.exists(self.database_name):
            choice = input(f"Database '{self.database_name}' already exists. Do you want to delete it? (y/n): ").lower()
            if choice == 'y':
                os.remove(self.database_name)
                print(f"Database '{self.database_name}' deleted.")
            else:
                print("Existing database was not deleted.")

    def open_database(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

    # Function to prompt the user for the DVD device path
    def enter_disk_path(self):
        default_path = "D:\\"
        dvd_device_path = input(f"Enter the path of the DVD device (default: {default_path}): ")
        return dvd_device_path if dvd_device_path else default_path

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
    
    def process_disks(self, num_disks):
        for disk_num in range(1, num_disks + 1):
            input(f"Insert DVD {disk_num} and press Enter when ready...")
            
            dvd_name = self.get_dvd_name(self.disk_path)

            if dvd_name:
                folders = self.list_folders(self.disk_path)

                if folders:
                    print(f"Folders on DVD '{dvd_name}':")
                    for folder in folders:
                        table_name = folder.replace("-", "_")
                        folder_path = os.path.join(self.disk_path, folder)
                        txt_files = self.get_txt_files(folder_path)

                        if txt_files:
                            print(f"Folder: {folder}")
                            for txt_file in txt_files:
                                txt_file_path = os.path.join(folder_path, txt_file)
                                self.create_table(table_name, txt_file_path)
                                self.insert_data(table_name, txt_file_path)
                            print("Table and data added.")
                        else:
                            print("No .txt files in this folder.")
                else:
                    print(f"No folders found on DVD '{dvd_name}'.")
            else:
                print(f"DVD not found at path '{self.disk_path}'.")

        # Commit the changes at the end
        self.conn.commit()

def main():

    database_name = 'chs_dvd.db'

    create_db = CreateDatabase(database_name)

    # Prompt to delete existing database
    create_db.delete_existing_database()

    create_db.open_database(database_name)
    
    num_disks = int(input("How many disks do you want to process?: "))
    create_db.disk_path = create_db.enter_disk_path()  # Set the disk path attribute

    create_db.process_disks(num_disks)  # Call the process_disks method
   
if __name__ == "__main__":
    main()
