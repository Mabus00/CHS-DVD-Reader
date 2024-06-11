''' 

module of common functions that are called more than once by different modules or that share other method calls
so it makes sense to keep them together

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

def process_report(data, csv_file_name, gui_text_box, current_database_folder, message=None):
    file_path = os.path.join(current_database_folder, csv_file_name)
    csv_file_path = f'{file_path}.csv'
    csv_mod_file_path = f'{file_path}_mod.csv'
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

def save_data_to_csv(data, message, csv_file_path):
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
