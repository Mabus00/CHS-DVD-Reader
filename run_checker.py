'''
Does the basic checks to ensure:
1. the East and West tables in each of the master and current databases have the same date; this to ensure the tables were created correctly.
2. the new current database is at least one month older than the master database; this to ensure the comparison between databases is valid.

If all good returns True and the process continues

Updated to streamline.

'''

# Import necessary modules
import common_utils as utils
import os
import csv

from build_database import BuildDatabase
from compare_databases import CompareDatabases
from compare_chart_numbers import CompareChartNumbers
from find_data_mismatches import FindDataMismatches
from check_folder_content import CheckFolderContent

from PyQt5.QtCore import QObject, pyqtSignal

# Define the RunChecker class
class RunChecker(QObject):
    finished = pyqtSignal(str, str, str)  # used to return self.database_path

    # Constructor for initializing the RunChecker object
    def __init__(self, ui, current_database, main_page_textbox, errors_textbox, chart_withdrawn_textbox, new_charts_textbox, new_editions_textbox, raster_target_folder, vector_target_folder):
        super().__init__() # call __init__ of the parent class chs_dvd_reader_main

        self.ui = ui
        self.master_database = None  # path to master database
        self.current_database = current_database

        # Create custom_signals connections
        self.main_page_textbox = main_page_textbox
        self.errors_textbox = errors_textbox
        self.chart_withdrawn_textbox = chart_withdrawn_textbox
        self.new_charts_textbox = new_charts_textbox
        self.new_editions_textbox = new_editions_textbox

        # database data input path
        self.current_database_path = ''

        self.raster_target_folder = raster_target_folder
        self.vector_target_folder = vector_target_folder

        self.master_database_conn = ''
        self.master_database_cursor = ''

        # create an ordered list of csv files so I can prioritize selection for the pdf report
        self.report_csv_files = [
            "misc_findings_type1.csv",
            "misc_findings_type2.csv",
            "new_editions.csv",
            "new_charts.csv",
            "charts_withdrawn.csv"
        ]
        
        # these files are pre-formatted versions of the above files; used for the gui windows and pdf report
        self.csv_mod_files = [
            "misc_findings_type1_mod.csv",
            "misc_findings_type2_mod.csv",
            "new_editions_mod.csv",
            "new_charts_mod.csv",
            "charts_withdrawn_mod.csv"
        ]

    # Method to compare databases
    def confirm_database_compliance(self, master_database_conn, current_database_conn):
        # Define table prefixes to be compared
        table_prefixes = ['EastDVD', 'WestDVD']
        # get the yyyymmdd for THE FIRST TABLE in both databases to conduct following two checks
        master_dates, current_dates = self.get_databases_yyyymmdd(master_database_conn, current_database_conn, table_prefixes)
        # Call the compare_tables_east_west_dates and compare_database_dates methods to perform table and databases comparisons
        match_result = self.compare_tables_east_west_dates(master_dates, current_dates)
        month_result = self.compare_database_dates(master_dates, current_dates)
        if match_result and month_result:
            self.main_page_textbox.emit("\nThe Master and Current databases are in compliance with the date matching criteria. ")
            return True
        else:
            self.main_page_textbox.emit("\nThe Master and Current databases are not in compliance with the date matching criteria. Please review the results and address the indicated issues.")
            return False

    def get_databases_yyyymmdd(self, master_database_conn, current_database_conn, table_prefixes):
        # Initialize dictionaries to store dates found in each database
        master_dates = {}
        current_dates = {}
        # get the first yyyymmdd prefix of each table in each database
        for prefix in table_prefixes:
            # Get the yyyymmdd from the first table in the master database
            master_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, master_database_conn)
            if master_yyyymmdd is not None:
                master_dates[prefix] = master_yyyymmdd
            # Get the yyyymmdd from the first table in the current database
            current_yyyymmdd = utils.get_first_table_yyyymmdd(prefix, current_database_conn)
            if current_yyyymmdd is not None:
                current_dates[prefix] = current_yyyymmdd
        return master_dates, current_dates

    def compare_tables_east_west_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix from THE FIRST TABLE in each database and ensure they match within the database
        match_result = False
        # Compare the EastDVD and WestDVD tables separately for both master and current databases
        if (
            master_dates.get('EastDVD') == master_dates.get('WestDVD') and
            current_dates.get('EastDVD') == current_dates.get('WestDVD')
        ):
            self.main_page_textbox.emit("\nEast & West DVD dates match within one or both databases.")
            match_result = True
        else:
            self.main_page_textbox.emit("\nEast & West DVD dates do not match within one or both databases.")
        return match_result

    def compare_database_dates(self, master_dates, current_dates):
        # compare the yyyymmdd prefix from THE FIRST TABLE of the EastDVD in each database and ensure the current database is at least a month older than the master database
        # only using EastDVD because the compare_tables_east_west_dates check comfirmed they're the same
        month_result = False
        if current_dates['EastDVD'] > master_dates['EastDVD'] :
            self.main_page_textbox.emit("\nCurrent East & West DVD dates are a month or more later than the Master Database dates.")
            month_result = True
        else:
            self.main_page_textbox.emit("\nCurrent East & West DVD dates are not a month or more later than the Master Database dates.")
        return month_result

    def delete_existing_files(self, file_path, files):
        for file_name in files:
            complete_path = os.path.join(file_path, file_name)
            if os.path.exists(complete_path):
                os.remove(complete_path)
                print(f"Deleted existing file: {complete_path}")

    def process_report(self, data, csv_file_name, gui_text_box, current_database_folder, message=None):
        file_path = os.path.join(current_database_folder, csv_file_name)
        csv_file_path = f'{file_path}.csv'
        csv_mod_file_path = f'{file_path}_mod.csv'
        # Save data to CSV file
        self.save_data_to_csv(data, message, csv_file_path)
        # Prepare data for GUI tab
        self.prep_csv_for_gui(csv_file_path)
        self.write_csv_mods_to_gui(csv_mod_file_path, gui_text_box)

    def get_column_headers(self, table_type, selected_cols):
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
    
    def save_data_to_csv(self, data, message, csv_file_path):
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

    def prep_csv_for_gui(self, csv_file_path):
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
                # if "misc" not in csv_file_path:
                # Check the number of columns in the row
                num_columns = len(row)
                # Keep rows with only one column
                if num_columns == 1:
                    if "RM" in row[0]:
                        # only show these columns
                        col_indices = [0,3,7]
                        table_type = "raster"
                        # set header row column tabs
                        col_headers = self.get_column_headers(table_type, col_indices)
                    else:
                        col_indices = [1,5,10]
                        table_type = "vector"
                        # set header row column tabs; needs an extra tab to line things up
                        col_headers = self.get_column_headers(table_type, col_indices)
                    if folder_title: # will only happen after the initial folder data is entered (I.e., the second go round)
                        csv_writer.writerow([])
                    folder_title = row
                    csv_writer.writerow(folder_title)
                    csv_writer.writerow(col_headers)
                # Keep columns 0, 4, and 5 for rows with more than one column
                else:
                    new_row = [row[col_indices[0]], row[col_indices[1]], row[col_indices[2]]]
                    csv_writer.writerow(new_row)
                # else:
                #     csv_writer.writerow(row)

    def write_csv_mods_to_gui(self, csv_mod_file_path, target_textbox):
        formatted_data = ''
        #current_folder_title = None
        # Open the CSV file for reading
        with open(csv_mod_file_path, 'r', newline='') as csv_file:
            # Create a CSV reader object for the input file
            csv_reader = csv.reader(csv_file)
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

    def run_checker(self, current_database_path, master_database):
        self.current_database_path = current_database_path
        self.master_database = master_database
        self.current_database = os.path.join(self.current_database_path, self.current_database) # actual path to current database
        # delete existing csv files so they can be updated; these files are used to fill tabs and create the pdf report
        self.delete_existing_files(self.current_database_path, self.report_csv_files)
        self.delete_existing_files(self.current_database_path, self.csv_mod_files)
        
        # FOUR PARTS TO RUN CHECKING
        # before starting confirm pre-build checks; checking whether a valid path was provided for new current database
        path_selected = utils.pre_build_checks(self.current_database, self.current_database_path, self.main_page_textbox)
        if path_selected:
            # establish database connections; operate under assumption that master_database won't be created each time widget is used
            self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database)
            self.current_database_conn, self.current_database_cursor = utils.get_database_connection(self.current_database)

            # instantiate generate_database and create the current month's database
            self.create_db = BuildDatabase(self.ui, self.current_database, self.main_page_textbox, self.raster_target_folder, self.vector_target_folder)
            self.create_db.generate_database(self.current_database_conn, self.current_database_cursor)

            # new process to check all .csv in vector folders to ensure they're the same
            print('here')

            # compliance = East and West tables within each database have the same date and the new current database is at least one month older than the master database
            # required to proceed further
            compliance = self.confirm_database_compliance(self.master_database_conn, self.current_database_conn)
            # check compliance; databases are dated correctly and are at least one month apart
            if not compliance:
                utils.show_warning_popup('You have error messages that need to be addressed.  See the Progress Report window.')
            else:
                # PART 1 OF 4 - check the .csv in the EAST and WEST folders against "Files" listed in the dB; confirm all files listed are present
                # e.g., for RM-ARC folder in the EAST folder, compare charts listed in the RM-ARC.csv to the database EastDVD_yyyymmdd_RM_ARC "File" list and report missing or extra
                # note - not needed for the master database; assumption is that this was confirmed in the previous month (the master in month X was the current in month X-1)
                self.check_folder_content = CheckFolderContent(self.current_database_cursor)
                missing_files, extra_files = self.check_folder_content.check_folders(self.current_database_path, self.raster_target_folder, self.vector_target_folder)
                # report charts_missing
                if missing_files or extra_files:
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                    # Determine which list to pass: missing_files or extra_files
                    # Process missing files if any
                    if missing_files:
                       self.process_report(missing_files, 'misc_findings_type2', self.errors_textbox, self.current_database_path)
                    # Process extra files if any
                    if extra_files:
                       self.process_report(extra_files, 'misc_findings_type2', self.errors_textbox, self.current_database_path)

                # PART 2 OF 4 - compare the folder content of the master and current databases and report new (i.e., not in master but in current) or missing / withdrawn
                # (i.e., in master but not in current) folders on the appropriate gui tab
                # run this first so you can ignore missing tables in PART 2 and 3
                self.compare_databases = CompareDatabases(self.master_database_cursor, self.current_database_cursor)
                # temp_tables_missing_in_current represent tables that have been removed; tables_missing_in_master represent tables that have been added in current
                # tables_master_temp and tables_current_temp have yyyymmdd removed; do this once and share with other modules
                # self.master_yyyymmdd and self.current_yyyymmdd are the extracted yyyymmdd for each
                tables_master_temp, temp_tables_missing_in_master, tables_current_temp, temp_tables_missing_in_current, self.master_yyyymmdd, self.current_yyyymmdd = self.compare_databases.compare_databases()
                # report withdrawn or new folders in current_database
                if temp_tables_missing_in_current or temp_tables_missing_in_master:
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                    error_messages = {
                        "missing_current": "Folders Removed",
                        "missing_master": "Folders Added",
                    }
                    for error_type, table_list in {"missing_current": temp_tables_missing_in_current, "missing_master": temp_tables_missing_in_master}.items():
                        if table_list:
                            message = error_messages[error_type]
                            self.process_report(table_list, 'misc_findings_type2', self.errors_textbox, self.current_database_path, message)

                # PART 3 OF 4 - compare master and current databases and report charts withdrawn and new charts
                # Remove tables_missing_from_current from tables_master so table content matches; no need to check tables_missing_in_master because these are newly added
                tables_master_temp = [table for table in tables_master_temp if table not in tables_current_temp]
                # instantiate CompareChartNumbers
                self.compare_chart_numbers = CompareChartNumbers(self.master_database_cursor, self.current_database_cursor)
                charts_withdrawn, new_charts = self.compare_chart_numbers.compare_chart_numbers(tables_master_temp, self.master_yyyymmdd, self.current_yyyymmdd)
                # Report missing charts on missing charts tab; can't use same process as above because of filenames and textbox identification
                if charts_withdrawn:
                   self.process_report(charts_withdrawn, 'charts_withdrawn', self.chart_withdrawn_textbox, self.current_database_path)
               # Report new charts on new charts tab
                if new_charts:
                   self.process_report(new_charts, 'new_charts', self.new_charts_textbox, self.current_database_path)
                
               # PART 4 OF 4 - find data mismatches
                # instantiate FindDataMismatches
                self.find_data_mismatches = FindDataMismatches(self.master_database_cursor, self.current_database_cursor)
                new_editions, misc_findings = self.find_data_mismatches.find_mismatches(tables_master_temp, self.master_yyyymmdd, self.current_yyyymmdd)
                # report new_editions
                if new_editions:
                   self.process_report(new_editions, 'new_editions', self.new_editions_textbox, self.current_database_path)
                # Report misc. findings (findings that couldn't be categorized as New Charts, New Editions or Charts Withdrawn)
                if misc_findings:
                    message = "Uncategorized Findings"
                    self.process_report(misc_findings, 'misc_findings_type1', self.errors_textbox, self.current_database_path, message)
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                
                # Print a message to indicate that the checker has run
                self.main_page_textbox.emit('\nThe Checker ran succesfully!')
        else:
            if not path_selected:
                utils.show_warning_popup("The path selected for the current month is invalid.")
            elif self.master_database == '':
                utils.show_warning_popup("You need to create a master database before conducting the current month comparison.")
            return
        
        # close the databases
        utils.close_database(self.master_database_conn)
        utils.close_database(self.current_database_conn)
        self.finished.emit(self.master_yyyymmdd, self.current_yyyymmdd)  # Emit the result through the signal

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
