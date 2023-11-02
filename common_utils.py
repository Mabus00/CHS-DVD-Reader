''' 

module of common functions that are called more than once by different modules

'''
import os
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import subprocess
import time
from datetime import datetime
import common_utils as utils

''' common functions used by more than one model / module'''
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
    # updates the selected text_browser with a simple message
    text_browser.insertPlainText(message + "\n")  # Append the message and a newline
    text_browser.ensureCursorVisible()

def clear_all_text_boxes(text_browsers):
    # Create a list of QTextBrowser widgets by inspecting the module
    for text_browser in text_browsers:
        text_browser.clear()

    print('all text boxes cleared')

''' Database common functions '''

def initialize_database(database_name, target_textbox):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    target_textbox.emit(f"Database '{database_name}' connected")
    return conn, cursor

def get_database_connection(database_name, target_textbox):
    conn, cursor = initialize_database(database_name, target_textbox)
    return conn, cursor

def confirm_database_deletion(rebuild_checkbox, database_name, target_textbox):
    # chs_dvd.db exists
    while not rebuild_checkbox.isChecked():
        show_warning_popup("Database exists. Check the 'Confirm deletion of database' box to proceed")
        return False
    else:
        delete_existing_database(database_name, target_textbox)
        return True

def confirm_data_path(text):
    if not text:
        show_warning_popup("Select data input path")
        return False
    return True
        
def delete_existing_database(database_name, target_textbox):
    os.remove(database_name)
    target_textbox.emit(f"Database '{database_name}' deleted.")

def close_database(target_textbox, database_conn, database_name):
    if database_conn:
        database_conn.close()
    target_textbox.emit(f'\n{database_name} closed.')

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
                dvd_name = dvd_name.replace('EAST', 'East').replace('WEST', 'West')
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
    with open(txt_file_path, 'r', errors='ignore') as txt_file:
        column_names = txt_file.readline().strip().split('\t')
        sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
        quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
        column_names_sql = ', '.join(quoted_column_names)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
        cursor.execute(create_table_sql)

# Function to insert data into a table from a text file
def insert_data(table_name, txt_file_path, cursor):
    with open(txt_file_path, 'r', errors='ignore') as txt_file:
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

''' Run Checker common functions '''

# Function to remove indicated portion from table_name
def remove_text(table_name, part_to_replace):
    parts = table_name.split('_')
    new_parts = [part for part in parts if part != part_to_replace]
    new_table_name = '_'.join(new_parts)
    return new_table_name

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

''' compare_database_tables common functions '''
def detect_column_changes(column_index, base_table, secondary_table, table_name):
        print(f'table name = {table_name}')
        # base_table = primary table against which the secondary_table is being compared
        # reset encountered chart numbers
        encountered_chart_numbers = set()

        # Create a set of chart numbers from current_data for faster lookup
        chart_numbers = set(row[column_index] for row in secondary_table)

        # Initialize a list to new charts and store missing chart numbers
        found_charts = []

        # Iterate through rows of master_data
        for i, row in enumerate(base_table):

            # get master_data chart name for the current row; remember the master is master!
            chart_number = row[column_index]

            # Check if the chart name from master_data is in current_data; if not add to missing_charts list
            if (chart_number not in chart_numbers) and (chart_number not in encountered_chart_numbers):
                # Append the missing chart name to the list
                found_charts.append(chart_number)
            
            # whether or not above condition fails add it to encountered_chart_numbers so we don't keep checking repeating master_chart_numbers
            if chart_number not in encountered_chart_numbers:
                # Add the chart name to the encountered_chart_names set
                encountered_chart_numbers.add(chart_number)

        # If there are missing charts for this table, add the table name and missing charts to the charts_withdrawn_result
        return (table_name, found_charts) if found_charts else None

def update_new_charts_tab(results, target_textbox, message):
    # tab reports for new and withdrawn charts
    for table_name, charts in results:
        target_textbox.emit(f"{message} {table_name}:")
        # Concatenate the chart numbers with commas
        chart_str = ', '.join(charts)
        target_textbox.emit(chart_str + '\n')

def update_new_editions_tab(results, current_yyyymmdd, target_textbox, message):
    for table_name, details in results:
        # add date to folder name
        temp = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
        target_textbox.emit(f"{message} {temp}:")
        if "RM" in table_name:
            for data in details:
                formatted_data = f"{data[1]:<12} {data[4]:>7}   {data[5]}"
                target_textbox.emit(formatted_data)
        else:
            for data in details:
                formatted_data = f"{data[1]:<12} {data[2]:<7}   {data[5]} "
                target_textbox.emit(formatted_data)
        target_textbox.emit("\n")

''' 
Raster table columns:
0 Chart 
1 File
2 Edn Date (dd-Mmm-yyyy)
3 Last NTM (yyyymmdd)
4 Edn#
5 Title

Vector table columns:
0 Chart
1 ENC
2 EDTN.UPDN = Edition Number.Update Number
3 ISDT = Issue Date (dd-Mmm-yyyy)
4 UADT = Update Application Date (dd-Mmm-yyyy)
5 Title

'''
def update_misc_findings_tab(results, current_yyyymmdd, target_textbox, message):
    # establish the type of misc_finding as the tab is used for different misc reports
    for result in results:
        if isinstance(result, tuple): # tuple is for folder with full details
            table_name, details = result
            # add date to folder name
            temp = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            target_textbox.emit(f"{message} {temp}:")
            if "RM" in table_name:
                for data in details:
                    formatted_data = f"{data[1]:<12} {data[4]:>7}   {data[5]}"
                    target_textbox.emit(formatted_data)
            else:
                for data in details:
                    formatted_data = f"{data[1]:<12} {data[2]:<7}   {data[5]} "
                    target_textbox.emit(formatted_data)
            target_textbox.emit("\n")
        else:
            # tab report for any errors.
            combined_results = "" 
            temp = utils.insert_text(result, current_yyyymmdd, pos_to_insert=1)
            if combined_results:
                # If there are already results in the combined string, add a comma and space
                combined_results += ", "
            combined_results += temp
            target_textbox.emit(f"{message} {combined_results} \n")
    
def convert_to_yyyymmdd(date_str):
    try:
        date_object = datetime.strptime(date_str, "%d-%b-%Y")
        return date_object.strftime("%Y%m%d")
    except ValueError:
        return None  # Handle invalid date strings gracefully

def tuple_to_list(tup):
    #Convert a tuple to a list.
    return list(tup)


