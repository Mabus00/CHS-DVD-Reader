''' 

module of common functions that are called more than once by different modules

'''
import os
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import subprocess
import time

def open_file_explorer(parent, input_path):
    input_path = QFileDialog.getExistingDirectory(parent, "Select Folder")
    input_path = input_path.replace("/", "\\")
    parent.setText(input_path)

def show_warning_popup(message):
    popup = QMessageBox()
    popup.setWindowTitle("Alert")
    popup.setText(message)
    popup.setIcon(QMessageBox.Warning)
    popup.exec_()

def update_text_browser(text_browser, message):
    text_browser.insertPlainText(message + "\n")  # Append the message and a newline
    text_browser.ensureCursorVisible()

''' Databse common functions '''

def initialize_database(database_name, text_browser_widget):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    update_text_browser(text_browser_widget, f"New '{database_name}' created and opened")
    return conn, cursor

def get_database_connection(database_name, text_browser_widget):
    conn, cursor = initialize_database(database_name, text_browser_widget)
    return conn, cursor

def delete_existing_database(database_name, text_browser_widget):
    if os.path.exists(database_name):
        os.remove(database_name)
        update_text_browser(text_browser_widget, f"Database '{database_name}' deleted.")

def close_database(text_browser_widget, create_database_conn):
    if create_database_conn:
        create_database_conn.close()
    update_text_browser(text_browser_widget, 'Database closed.')

# Function to list folders in the DVD path
def list_folders(folder_path):
    if os.path.exists(folder_path):
        folders = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
        return folders
    else:
        return []

# Function to get a list of .txt files in a folder
def get_txt_files(folder_path):
    txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]
    return txt_files
    
# Function to get the DVD name using the disk path; retries introduced because USB connected DVD readers can lag
def get_dvd_name(input_data_path, max_retries=5, retry_interval=1):
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Attempt to retrieve DVD name
            output = subprocess.check_output(f'wmic logicaldisk where DeviceID="{input_data_path[:2]}" get volumename', text=True)
            lines = output.strip().split('\n')
            dvd_name = lines[2] if len(lines) > 1 else ''
            if dvd_name:
                print(f'Number of retries = {retry_count}') #number of retries
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

# Function to create a table with column names from a text file
def create_table(table_name, txt_file_path, cursor):
    with open(txt_file_path, 'r') as txt_file:
        column_names = txt_file.readline().strip().split('\t')
        sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
        quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
        column_names_sql = ', '.join(quoted_column_names)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
        cursor.execute(create_table_sql)

# Function to insert data into a table from a text file
def insert_data(table_name, txt_file_path, cursor):
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