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
        # using the column_index to identify the comparator, detect changes in cell content (i.e., missing cell content)
        # base_table = primary table against which the secondary_table is being compared
        # reset encountered column content
        encountered_column_content = set()
        # Create a set of cell content from secondary_table for faster lookup
        column_content = set(row[column_index] for row in secondary_table)
        # Initialize a list to store the rows where missing cell content has been found
        found_rows = []
        # Iterate through rows of master_data
        for i, row in enumerate(base_table):
            # get base_table cell content for the current row
            cell_content = row[column_index].strip()
            # Check if the cell content from base_table is in secondary_table
            if (cell_content not in column_content) and (cell_content not in encountered_column_content):
                # Append the row to the list
                found_rows.append(row)
            # whether or not above condition fails add it to encountered_column_content so we don't keep checking repeating cell content
            if cell_content not in encountered_column_content:
                # Add the cell content to the encountered_column_content set
                encountered_column_content.add(cell_content)
        return (table_name, found_rows) if found_rows else None

def update_new_editions_tab(results, current_yyyymmdd, target_textbox, message):
    target_textbox.emit(f"{message}\n")
    for table_name, details in results:
        # add date to folder name
        temp = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
        target_textbox.emit(f"{temp}:")
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

def get_column_headers(table_type, selected_cols):
    # return the selected column headers
    raster_table_columns = ["Chart", "File", "Edn Date", "Last NTM", "Edn#", "Title"]
    vector_table_columns = ["Chart", "ENC", "EDTN", "ISDT", "UADT", "Title"]
    # Select appropriate columns based on table_type
    if table_type == "raster":
        selected_columns = [raster_table_columns[idx] for idx in selected_cols if idx < len(raster_table_columns)]
    elif table_type == "vector":
        selected_columns = [vector_table_columns[idx] for idx in selected_cols if idx < len(vector_table_columns)]
    else:
        return []  # Return an empty list for an invalid table_type
    return selected_columns

def convert_to_html(title, col_headers, data):
    # Start building the HTML string
    html = f"<h2>{title}</h2>\n<table border='1'>\n"

    # Create the header row
    html += "<tr>"
    for header in col_headers:
        html += f"<th>{header}</th>"
    html += "</tr>\n"

    # Add data rows
    for row in data:
        html += "<tr>"
        for column in row.split('\t'):
            html += f"<td>{column}</td>"
        html += "</tr>\n"

    # Close the table tag
    html += "</table>"
    
    return html

def update_selected_tab(results, current_yyyymmdd, target_textbox, message, file_to_open = 'misc_findings_type2.txt'):
    # Tab report for all reports. Type 1 is for detailed results (hence tuple) whereas Type 2 is simple results (non-tuple) (default)
    formatted_data = ""
    # Establish the type of misc_finding as the tab is used for different misc reports; use tuple
    for result in results:
        if isinstance(result, tuple): 
            # tuple indicates detailed results and is for type 1 report
            write_method = 'w'
            if formatted_data == "":
                # add message which acts as section header
                formatted_data += message + "\n"
            folder_name, details = result
            # Add date to folder name
            if current_yyyymmdd is not None:
                folder_name = utils.insert_text(folder_name, current_yyyymmdd, pos_to_insert=1)
            # add folder_name which acts as table header
            formatted_data += "\n" + folder_name + ":"
            if "RM" in folder_name:
                col_indices = [0,4,5]
                table_type = "raster"
            else:
                col_indices = [1,2,5]
                table_type = "vector"
            col_headers = get_column_headers(table_type, col_indices)
            header_line  = f"{col_headers[0].ljust(12)}\t{col_headers[1].ljust(8)}\t{col_headers[2]}"
            # add column headers
            formatted_data += "\n" + header_line
            for data in details:
                temp = f"{data[col_indices[0]].ljust(12)}\t{data[col_indices[1]].ljust(8)}\t{data[col_indices[2]]}"
                formatted_data += "\n" + temp
            formatted_data += "\n"
        else:
            # type 2 report is a simple report that contains non-tuple results
            # write method is append because I want to track all type 2 reports in one document; there could be more than call to this method
            write_method = 'a'
            if formatted_data == "":
                    formatted_data += "\n" + message
            # add folder name to combined_results
            if current_yyyymmdd is not None:
                folder_name = utils.insert_text(result, current_yyyymmdd, pos_to_insert=1)
            formatted_data += "\n" + folder_name
            formatted_data += "\n" 

    # Writting to the selected file then sending formatted_data to target_textbox.emit()
    with open(file_to_open, write_method) as file:
        file.write(f"{formatted_data}\n")
        target_textbox.emit(formatted_data)
    
def convert_to_yyyymmdd(date_str):
    try:
        date_object = datetime.strptime(date_str, "%d-%b-%Y")
        return date_object.strftime("%Y%m%d")
    except ValueError:
        return None  # Handle invalid date strings gracefully

def tuple_to_list(tup):
    #Convert a tuple to a list.
    return list(tup)


def yes_or_no_popup(message):
    reply = QMessageBox()
    reply.setText(message)
    reply.setStandardButtons(QMessageBox.StandardButton.Yes | 
                        QMessageBox.StandardButton.No)
    return reply.exec()

def rename_database(old_database_name, new_database_name):
    print('making current the new master database')
    # Replace 'current_database.db' and 'master_database.db' with your actual file names
    os.rename(old_database_name, new_database_name)
