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
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import time
from tqdm import tqdm
import sys

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

# not used but keep
def yes_or_no_popup(message):
    reply = QMessageBox()
    reply.setText(message)
    reply.setStandardButtons(QMessageBox.StandardButton.Yes | 
                        QMessageBox.StandardButton.No)
    return reply.exec()

def find_folder(starting_directory, target_folder_name):
    # Recursively searches for a folder with a specific name starting from the given directory.
    for root, dirs, files in os.walk(starting_directory):
        for dir_name in dirs:
            if dir_name == target_folder_name:
                return os.path.join(root, dir_name)
    return None

# similar method in
def pre_build_checks(database_path, database_folder, textbox):
    path_selected = True
    # delete if necessary; database will be rebuilt
    if os.path.exists(database_path):
        delete_existing_database(database_path, textbox)
    # ensure user has selected a data input path
    if not confirm_data_path(database_folder):
        path_selected = False
    return path_selected

def initialize_database(database_path, target_textbox):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    target_textbox.emit(f"Database '{database_path}' connected")
    return conn, cursor
    
def get_database_connection(database_path, target_textbox):
    conn, cursor = initialize_database(database_path, target_textbox)
    return conn, cursor

def close_database(target_textbox, database_conn, database_path):
    if database_conn:
        database_conn.close()
    target_textbox.emit(f'\n{database_path} closed.')

def long_running_task():
    for _ in tqdm(range(100), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        time.sleep(0.1)  # Simulate work being done