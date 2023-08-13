import sqlite3
import os
import subprocess

def get_dvd_name():
    output = subprocess.check_output(['wmic', 'logicaldisk', 'where', 'drivetype=5', 'get', 'volumename'], text=True)
    lines = output.strip().split('\n')
    dvd_name = lines[2] if len(lines) > 1 else ''
    return dvd_name.strip() if dvd_name else None

def list_folders(dvd_path):
    if os.path.exists(dvd_path):
        folders = [item for item in os.listdir(dvd_path) if os.path.isdir(os.path.join(dvd_path, item))]
        return folders
    else:
        return []

def create_table(cursor, table_name, txt_file_path):
    with open(txt_file_path, 'r') as txt_file:
        column_names = txt_file.readline().strip().split('\t')
        sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
        quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
        column_names_sql = ', '.join(quoted_column_names)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
        cursor.execute(create_table_sql)

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

def get_txt_files(folder_path):
    txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]
    return txt_files

def main():
    dvd_name = get_dvd_name()
    dvd_device_path = "D:\\"

    # Connect to the SQLite database
    conn = sqlite3.connect('chs_dvd.db')
    cursor = conn.cursor()

    if dvd_name:

        folders = list_folders(dvd_device_path)

        if folders:
            print(f"Folders on DVD '{dvd_name}':")
            for folder in folders:
                if folder.startswith(('R', 'V')):
                    table_name = folder.replace("-", "_")  # Replace hyphens with underscores
                    folder_path = os.path.join(dvd_device_path, folder)
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
        print("No DVD found.")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

   
if __name__ == "__main__":
    main()
