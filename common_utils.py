''' 

module of common functions that are called more than once by different modules

'''
import os
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import subprocess
import time
from datetime import datetime
import csv
import chardet

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

def initialize_database(database_path, target_textbox):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    target_textbox.emit(f"Database '{database_path}' connected")
    return conn, cursor

def get_database_connection(database_path, target_textbox):
    conn, cursor = initialize_database(database_path, target_textbox)
    return conn, cursor

def confirm_database_deletion(rebuild_checkbox, database_path, target_textbox):
    # chs_dvd.db exists
    while not rebuild_checkbox.isChecked():
        show_warning_popup("Database exists. Check the 'Confirm deletion of database' box to proceed")
        return False
    else:
        delete_existing_database(database_path, target_textbox)
        return True

def confirm_data_path(text):
    if not text:
        show_warning_popup("Select data input path")
        return False
    return True
        
def delete_existing_database(database_path, target_textbox):
    os.remove(database_path)
    target_textbox.emit(f"Database '{database_path}' deleted.")

def close_database(target_textbox, database_conn, database_path):
    if database_conn:
        database_conn.close()
    target_textbox.emit(f'\n{database_path} closed.')

# Function to list folders in the DVD path
def list_folders(folder_path):
    if os.path.exists(folder_path):
        folders = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
        return folders
    else:
        return []

# Function to get a list of .txt or .csv files in a folder
def get_files(folder_path, file_extension):
    files = [file for file in os.listdir(folder_path) if file.endswith(f".{file_extension}")]
    return files

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

def process_report(data, csv_file_name, gui_text_box, current_database_path, message=None):
    csv_file_path = f'{csv_file_name}.csv'
    csv_mod_file_path = f'{csv_file_name}_mod.csv'
    # Save data to CSV file
    save_data_to_csv(data, message, csv_file_path)
    # Prepare data for GUI tab
    prep_csv_for_gui(csv_file_path)
    write_csv_mods_to_gui(csv_mod_file_path, gui_text_box)

# Function to detect file encoding using chardet
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    encoding_result = chardet.detect(rawdata)
    return encoding_result['encoding'].lower()  # Convert to lowercase

# Function to create a table with column names from a .txt or .csv file
def create_table(table_name, file_path, cursor, file_extension):
    if file_extension == 'txt':
        with open(file_path, 'r', errors='ignore') as txt_file:
            column_names = txt_file.readline().strip().split('\t')
    else:
        # Detect the encoding of the file
        detected_encoding = detect_encoding(file_path)
        #print(f'create_table detected encoding = {detected_encoding}')
        try:
            # Open the file using the detected encoding
            with open(file_path, 'r', newline='', encoding=detected_encoding) as csv_file:
                csv_reader = csv.reader(csv_file)
                # Read the first row to get column names
                column_names = next(csv_reader)
                sanitized_column_names = [name.replace(".", "").strip() for name in column_names]
                quoted_column_names = [f'"{name}"' for name in sanitized_column_names]
                column_names_sql = ', '.join(quoted_column_names)
                create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_names_sql})"
                cursor.execute(create_table_sql)
        except UnicodeDecodeError as e:
            print(f"Error in create_table decoding file '{file_path}': {e}")
            # Handle the error as needed
   
# Function to insert data into a table from a .txt or .csv file
def insert_data(table_name, file_path, cursor, file_extension):
    try:
        if file_extension == 'txt':
            with open(file_path, 'r', errors='ignore') as txt_file:
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
        elif file_extension == 'csv':
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
                            data = row
                            placeholders = ', '.join(['?'] * len(data))
                            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                            cursor.execute(insert_sql, data)
            except UnicodeDecodeError as e:
                print(f"Error in insert_data decoding file '{file_path}': {e}")
                # Handle the error as needed
        else:
            raise ValueError("Unsupported file extension in insert_data.")
    # following is to capture errors if and when they occur
    except sqlite3.OperationalError as e:
        print(f"SQLite operational error: {e}")
    except Exception as e:
        print(f"Error inserting data: {e}")

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

def detect_column_changes(column_index, base_table, secondary_table, table_name):
    # using the column_index to identify the comparator, detect changes in cell content (i.e., missing cell content)
    # base_table = primary table against which the secondary_table is being compared
    # reset encountered column content
    encountered_column_content = []
    # Create a list of tuples containing (row_index, cell_content) from secondary_table for comparison
    column_content = [(i, row[column_index].strip()) for i, row in enumerate(secondary_table)]
    # Initialize a list to store the rows where missing cell content has been found
    found_rows = []
    # Iterate through rows of base_table
    for i, row in enumerate(base_table):
        # get base_table cell content for the current row
        cell_content = row[column_index].strip()
        # Check if the cell content from base_table is not in secondary_table
        if (cell_content not in [content[1] for content in column_content]) and (cell_content not in [content[1] for content in encountered_column_content]):
            # Append the row to the list
            found_rows.append(row)
        # whether or not above condition fails add it to encountered_column_content so we don't keep checking repeating cell content
        if cell_content not in [content[1] for content in encountered_column_content]:
            # Add the cell content to the encountered_column_content list
            encountered_column_content.append((i, cell_content))
    # returns a tuple consisting of the table_name and a list of tuples with the row data
    return (table_name, found_rows) if found_rows else None

''' 
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

def prep_csv_for_gui(csv_file_path):
    # extracts .csv file data and keeps only those fields needed for gui tab display
    # these files will also be used to create .pdf report but note the order of columns is specifically for the gui; need to keep title last so everything looks good and lined up
    # Extract the file name and extension from the input file path
    file_name, file_extension = os.path.splitext(csv_file_path)
    # Construct the output file path by appending "_mod" before the file extension
    output_csv_file = file_name + "_mod" + file_extension
    folder_title = None
    # Open the input CSV file for reading and the output CSV file for writing
    with open(csv_file_path, 'r', newline='') as input_file, open(output_csv_file, 'w', newline='') as output_file:
        # Create a CSV reader object for the input file
        csv_reader = csv.reader(input_file)
        # Create a CSV writer object for the output file
        csv_writer = csv.writer(output_file)
        # Iterate over each row in the CSV file
        for row in csv_reader:
            if "misc" not in csv_file_path:
                # Check the number of columns in the row
                num_columns = len(row)
                # Keep rows with only one column
                if num_columns == 1:
                    if "RM" in row[0]:
                        # only show these columns
                        col_indices = [0,3,7]
                        table_type = "raster"
                        # set header row column tabs
                        col_headers = get_column_headers(table_type, col_indices)
                    else:
                        col_indices = [1,5,10]
                        table_type = "vector"
                        # set header row column tabs; needs an extra tab to line things up
                        col_headers = get_column_headers(table_type, col_indices)
                    if folder_title: # will only happen after the initial folder data is entered (I.e., the second go round)
                        csv_writer.writerow([])
                    folder_title = row
                    csv_writer.writerow(folder_title)
                    csv_writer.writerow(col_headers)
                # Keep columns 0, 4, and 5 for rows with more than one column
                else:
                    new_row = [row[col_indices[0]], row[col_indices[1]], row[col_indices[2]]]
                    csv_writer.writerow(new_row)
            else:
                csv_writer.writerow(row)

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

def merge_files(file1_path, file2_path):
    if os.path.exists(file1_path) and os.path.exists(file2_path):
        with open(file1_path, "a") as file1, open(file2_path, "r") as file2:
            content2 = file2.read()

            file1.write("\n" + content2)
        os.remove(file2_path)
    return file1

def delete_existing_files(files):
    for file_name in files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted existing file: {file_name}")

def save_data_to_csv(data, message, csv_file_path):
    """
    Save the given data to a CSV file.

    Args:
    - data (list): The data to be saved.
    - message (str): The message to be written at the beginning of the file.
    - csv_file_path (str): The file path of the CSV file to be created.
    """
    # Open the CSV file for writing
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write the message at the beginning of the file (only for misc report type 2)
        if message:
            writer.writerow([message])
        # Write each entry of the data list to the CSV file
        for entry in data:
            # Check if the entry is a tuple (data structure) or a single value
            if isinstance(entry, tuple):
                text, data_list = entry
                # Write the text as a header
                if text:
                    writer.writerow([text])
                # Write each row in the data list as a separate record
                for row in data_list:
                    row_stripped = [str(cell).strip() for cell in row]
                    writer.writerow(row_stripped)
            else:
                writer.writerow([entry])  # Write a single value to the CSV file

def write_csv_mods_to_gui(csv_mod_file_path, target_textbox):
    formatted_data = ''
    #current_folder_title = None
    # Open the CSV file for reading
    with open(csv_mod_file_path, 'r', newline='') as csv_file:
        # Create a CSV reader object for the input file
        csv_reader = csv.reader(csv_file)
        if "misc" in csv_mod_file_path:
            # Read each row of the CSV file
            for i, row in enumerate(csv_reader):
                if i == 0:
                    formatted_data = f"{row[0]}\n"  # Extract folder title from the first row
                else:
                    formatted_data += str(row[0]) + '\n'  # Process data rows
        else:
            # Read each row of the CSV file
            for i, row in enumerate(csv_reader):
                if len(row) == 1: # this is a folder title
                    folder_title = row[0]
                    formatted_data += f"{folder_title}\n"  # Add folder title
                else:  # Ensure there is a folder title before adding data
                    if row:
                        if not row[1]:
                            row[1] = "            "
                        if "RM" in folder_title:
                            if any(any(char.isdigit() for char in string) for string in row): # digits means it's a line of data
                                formatted_data += row[0] + '\t\t' + row[1] + '\t\t' + row[2] + '\n'
                            else: # no digits means it's a header row
                                formatted_data += row[0] + '\t' + row[1] + '\t\t' + row[2] + '\n'
                        else:
                            if any(any(char.isdigit() for char in string) for string in row): # digits means it's a line of data
                                formatted_data += row[0] + '\t\t' + row[1] + '\t' + row[2] + '\n'
                            else: # no digits means it's a header row
                                formatted_data += row[0] + '\t' + row[1] + '\t\t' + row[2] + '\n'
                    else:
                        formatted_data += '\n'
    # Send formatted_data to target_textbox.emit()
    target_textbox.emit(formatted_data)
