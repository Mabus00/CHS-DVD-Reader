'''
Code that creates the sqlite database reading from CHS DVDs inserted in DVD reader.
Intent is that user will only load one CHS East and one CHS West DVD.
This forms the database. Later code will read current CHS DVDs and compare data to what is in database
to check for errors, new charts, new editions, charts withdrawn and potential errors.

Intent later is to modify this code to also read from a .zip file (this is how the monthly data is received).

'''

import sqlite3
import os
import subprocess

# Function to delete the existing database if user chooses
def delete_existing_database(database_name):
    if os.path.exists(database_name):
        choice = input(f"Database '{database_name}' already exists. Do you want to delete it? (y/n): ").lower()
        if choice == 'y':
            os.remove(database_name)
            print(f"Database '{database_name}' deleted.")
        else:
            print("Existing database was not deleted.")

# Function to prompt the user for the DVD device path
def enter_disk_path():
    default_path = "D:\\"
    dvd_device_path = input(f"Enter the path of the DVD device (default: {default_path}): ")
    return dvd_device_path if dvd_device_path else default_path

# Function to get the DVD name using the disk path
def get_dvd_name(disk_path):
    output = subprocess.check_output(f'wmic logicaldisk where DeviceID="{disk_path[:2]}" get volumename', text=True)
    lines = output.strip().split('\n')
    dvd_name = lines[2] if len(lines) > 1 else ''
    return dvd_name.strip() if dvd_name else None

# Function to list folders in the DVD path
def list_folders(dvd_path):
    if os.path.exists(dvd_path):
        folders = [item for item in os.listdir(dvd_path) if os.path.isdir(os.path.join(dvd_path, item))]
        return folders
    else:
        return []

# Function to create a table with column names from a text file
def create_table(cursor, table_name, txt_file_path):
    with open(txt_file_path, 'r') as txt_file:
        column_names = txt_file.readline().strip().split('\t')
        sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
        quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
        column_names_sql = ', '.join(quoted_column_names)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
        cursor.execute(create_table_sql)

# Function to insert data into a table from a text file
def insert_data(cursor, table_name, txt_file_path):
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
            cursor.execute(insert_sql, data)

# Function to get a list of .txt files in a folder
def get_txt_files(folder_path):
    txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]
    return txt_files

def main():
    database_name = 'chs_dvd.db'

    # Prompt to delete existing database
    delete_existing_database(database_name)

    # Get the disk path from the user
    disk_path = enter_disk_path()

    # Connect to the SQLite database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    num_disks = int(input("How many disks do you want to process?: "))

    # Loop through disks and copy data to sqlite database
    for disk_num in range(1, num_disks + 1):
        input(f"Insert DVD {disk_num} and press Enter when ready...")
        
        dvd_name = get_dvd_name(disk_path)

        if dvd_name:
            folders = list_folders(disk_path)

            if folders:
                print(f"Folders on DVD '{dvd_name}':")
                for folder in folders:
                    table_name = folder.replace("-", "_")  # Replace hyphens with underscores; sqlite doesn't work with hyphens
                    folder_path = os.path.join(disk_path, folder)
                    txt_files = get_txt_files(folder_path)

                    if txt_files:
                        print(f"Folder: {folder}")
                        for txt_file in txt_files:
                            txt_file_path = os.path.join(folder_path, txt_file)
                            create_table(cursor, table_name, txt_file_path)
                            insert_data(cursor, table_name, txt_file_path)
                        print("Table and data added.")
                    else:
                        print("No .txt files in this folder.")
            else:
                print(f"No folders found on DVD '{dvd_name}'.")
        else:
            print(f"DVD not found at path '{disk_path}'.")

        # Commit the changes and close the connection
        conn.commit()
    
    # Close the connection after processing all disks
    conn.close()
   
if __name__ == "__main__":
    main()
