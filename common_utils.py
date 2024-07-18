''' 

Module of common functions that are called more than once by different modules or that share other method calls
so it makes sense to keep them together

Raster table columns:
0 BSB Chart 
1 File
2 Edition Date (yyyymmdd)
3 Last NTM (yyyymmdd)
4 Raster Edition
5 KAP Files
6 Region
7 Title

Vector table columns:
0 Collection
1 Cell Name
2 EDTN = Edition Number
3 UPDN = Update Number
4 ISDT = Issue Date (dd-Mmm-yyyy)
5 UADT = Update Application Date (dd-Mmm-yyyy)
6 SLAT = Southern Lattitude
7 WLON = Western Longitude
8 NLAT= Northern Lattitude
9 ELON = Eastern Longitude
10 Title

'''

import os
import sqlite3
from PyQt5.QtWidgets import QMessageBox
import csv
import chardet

def show_warning_popup(message):
    popup = QMessageBox()
    popup.setWindowTitle("Alert")
    popup.setText(message)
    popup.setIcon(QMessageBox.Warning)
    popup.exec_()

def confirm_data_path(text):
    if not text:
        show_warning_popup("Select data input path")
        return False
    return True
        
def delete_existing_database(database_path, target_textbox):
    os.remove(database_path)
    target_textbox.emit(f"Database '{database_path}' deleted.")
    
# Function to detect file encoding using chardet
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    encoding_result = chardet.detect(rawdata)
    return encoding_result['encoding'].lower()  # Convert to lowercase

# Function to insert data into a table from a .txt or .csv file
def insert_data(table_name, file_path, cursor, file_extension):        
    try: # Detect the encoding of the file
        detected_encoding = detect_encoding(file_path)
        #print(f'insert_data {table_name} detected encoding = {detected_encoding}')
        with open(file_path, 'r', newline='', encoding=detected_encoding) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # Skip the first two lines (column names and extra line if needed)
            next(csv_reader)  
            for row in csv_reader:
                if row:  # Check if the row is not empty; there seems to be an empty row at the end of the data
                    # Process the non-empty row
                    if 'Cancel_Annuler' not in row[0]: 
                        data = row
                        placeholders = ', '.join(['?'] * len(data))
                        insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                        cursor.execute(insert_sql, data)
    except UnicodeDecodeError as e:
        print(f"Error in insert_data decoding file '{file_path}': {e}")
        # Handle the error as needed
    # following is to capture errors if and when they occur
    except sqlite3.OperationalError as e:
        print(f"SQLite operational error: {e}")
    except Exception as e:
        print(f"Error inserting data: {e}")

def insert_text(table_name, text, pos_to_insert):
    parts = table_name.split('_')
    # Check if the specified part_to_replace is within the valid range
    if 0 <= pos_to_insert < len(parts) - 1:
        parts.insert(pos_to_insert, text)  # Replace the specified part with an empty string
        # Filter out empty parts and join with underscores
        new_table_name = '_'.join(filter(None, parts))
    return new_table_name  # Join all parts with underscore

def extract_yyyymmdd(table_name):
    return table_name.split('_')[1]

# Method to get the yyyymmdd from the first table with a given prefix in a database connection
def get_first_table_yyyymmdd(prefix, database_conn):
    cursor = database_conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{prefix}%'")
    tables = cursor.fetchall()
    if tables:
        first_table = tables[0][0]
        return extract_yyyymmdd(first_table)
    return None

def get_column_headers(table_type, selected_cols):
    # return the selected column headers
    raster_table_columns = ["BSB Chart", "File", "Edition Date", "Last NTM", "Raster Edition", "Kap FIles", "Region", "Title"]
    vector_table_columns = ["Collection", "Cell_Name", "EDTN", "UPDN", "ISDT", "UADT", "SLAT", "WLON", "NLAT", "ELON", "Title"]
    # Select appropriate columns based on table_type
    if table_type == "raster":
        selected_columns = [raster_table_columns[idx] for idx in selected_cols if idx < len(raster_table_columns)]
    elif table_type == "vector":
        selected_columns = [vector_table_columns[idx] for idx in selected_cols if idx < len(vector_table_columns)]
    else:
        return []  # Return an empty list for an invalid table_type
    return selected_columns


# not used but keep
def yes_or_no_popup(message):
    reply = QMessageBox()
    reply.setText(message)
    reply.setStandardButtons(QMessageBox.StandardButton.Yes | 
                        QMessageBox.StandardButton.No)
    return reply.exec()

# not used but keep
def merge_files(file1_path, file2_path):
    if os.path.exists(file1_path) and os.path.exists(file2_path):
        with open(file1_path, "a") as file1, open(file2_path, "r") as file2:
            content2 = file2.read()

            file1.write("\n" + content2)
        os.remove(file2_path)
    return file1



def find_folder(starting_directory, target_folder_name):
    # Recursively searches for a folder with a specific name starting from the given directory.
    for root, dirs, files in os.walk(starting_directory):
        for dir_name in dirs:
            if dir_name == target_folder_name:
                return os.path.join(root, dir_name)
    return None