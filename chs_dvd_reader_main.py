'''
Main CONTROLLER for app.  There are three sub controllers:
1. sub-controller to build_database
2. sub-controller to run_checker.
3. sub-controller to build pdf report.

I chose to use custom signals and slots to provide greater seperation of concerns and looser coupling.
I could have gone directly from the UI signal to the slot but chose this instead.
Note that I control almost all signals from here.  I could have done that in utils but i felt if went against the MVC architecture.

tables = CHS DVD folders

Signals are controlled from here only.

VIEW = chs_dvd_gui

'''

import sys
import inspect
import os
import common_utils as utils
import glob
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals, RunCheckerSignals, NewChartsSignals, NewEditionsSignals, WithdrawnSignals, ErrorsSignals
from build_database import BuildDatabase
from run_checker import RunChecker
from compare_databases import CompareDatabases
from compare_chart_numbers import CompareChartNumbers
from find_data_mismatches import FindDataMismatches
from check_folder_content import CheckFolderContent
from create_pdf_report import PDFReport

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # create list of text browsers so they can be cleared en masse
        self.text_browsers = [obj for name, obj in inspect.getmembers(self.ui) if isinstance(obj, QTextEdit)]

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

        # set database connections
        self.master_database_conn = ""
        self.master_database_cursor = ""
        self.current_database_conn = ""
        self.current_database_cursor = ""

        self.master_yyyymmdd = ""
        self.current_yyyymmdd = ""

        # set master database input path to nothing; user must select path manually 
        self.master_database_folder = ""
        self.master_database_path = "master_database.db"

        # set current month database input path to nothing; user must select path manually 
        self.current_database_folder = ""
        self.current_database_path = "current_database.db"

        # target folders to find to process data
        self.raster_target_folder = 'BSBCHART'
        self.vector_target_folder = 'ENC_ROOT'

        # Create an instance of RunCheckerSignals
        self.run_checker_signals = RunCheckerSignals()

        # Create an instance of NewChartsSignals
        self.new_charts_signals = NewChartsSignals()

        # Create an instance of NewChartsSignals
        self.new_editions_signals = NewEditionsSignals()

        # Create an instance of ErrorsSignals
        self.errors_signals = ErrorsSignals()

        # Create an instance of WithdrawnSignals
        self.charts_withdrawn_signals = WithdrawnSignals()

        # Create an instance of CreateDatabaseSignals
        self.database_signals = CreateDatabaseSignals()

        # Connect UI signals to custom signals using object names
        # run checker tab
        self.ui.selectCheckerDataPathButton.clicked.connect(self.run_checker_signals.data_input_path_button.emit)
        self.ui.runCheckerButton.clicked.connect(self.run_checker_signals.run_checker_button.emit)
        self.ui.createPDFReportButton.clicked.connect(self.run_checker_signals.create_pdf_report_button.emit)
        # create database tab
        self.ui.selectDataPathButton.clicked.connect(self.database_signals.database_input_path_button.emit)
        self.ui.buildDatabaseButton.clicked.connect(self.database_signals.build_database_button.emit)

        # Connect custom signals to slots
        # run checker tab
        self.run_checker_signals.data_input_path_button.connect(lambda: self.open_file_explorer(self.ui.checker_data_input_path, self.current_database_path))
        self.run_checker_signals.run_checker_button.connect(self.run_checker)
        self.run_checker_signals.create_pdf_report_button.connect(self.create_pdf_report)
        # create database tab
        self.database_signals.database_input_path_button.connect(lambda: self.open_file_explorer(self.ui.database_input_path, self.master_database_folder))
        self.database_signals.build_database_button.connect(self.build_database)

        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.run_checker_signals.run_checker_textbox.connect(lambda message: self.update_text_browser(self.ui.runCheckerTextBrowser, message))
        self.errors_signals.errors_textbox.connect(lambda message: self.update_text_browser(self.ui.errorsTextBrowser, message))
        self.new_charts_signals.new_charts_textbox.connect(lambda message: self.update_text_browser(self.ui.newChartsTextBrowser, message))
        self.new_editions_signals.new_editions_textbox.connect(lambda message: self.update_text_browser(self.ui.newEditionsTextBrowser, message))
        self.charts_withdrawn_signals.chart_withdrawn_textbox.connect(lambda message: self.update_text_browser(self.ui.chartsWithdrawnTextBrowser, message))
        self.database_signals.create_database_textbox.connect(lambda message: self.update_text_browser(self.ui.createDatabaseTextBrowser, message))

    def initialize_database(self, database_path, target_textbox):
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        target_textbox.emit(f"Database '{database_path}' connected")
        return conn, cursor

    def get_database_connection(self, database_path, target_textbox):
        conn, cursor = self.initialize_database(database_path, target_textbox)
        return conn, cursor

    def open_file_explorer(self, parent, input_path):
        input_path = QFileDialog.getExistingDirectory(parent, "Select Folder")
        input_path = input_path.replace("/", "\\")
        parent.setText(input_path)

    def update_text_browser(self, text_browser, message):
        # updates the selected text_browser with a simple message
        text_browser.insertPlainText(message + "\n")  # Append the message and a newline
        text_browser.ensureCursorVisible()

    def close_database(self, target_textbox, database_conn, database_path):
        if database_conn:
            database_conn.close()
        target_textbox.emit(f'\n{database_path} closed.')

    def build_database(self):
        # instantiate create_database and pass instance of database_name, etc...
        self.master_database_folder = self.ui.database_input_path.text() # path to master database folder
        self.master_database_path = os.path.join(self.master_database_folder, self.master_database_path) # actual path to master database
        self.create_db = BuildDatabase(self.master_database_path, self.ui.rebuild_checkbox, self.database_signals.create_database_textbox, self.master_database_folder, self.raster_target_folder, self.vector_target_folder)
        # confirm that pre-build checks are met before proceeding
        if all(self.create_db.pre_build_checks()):
            # establish database connections; operate under assumption that master_database won't be created each time widget is used
            # note that this can't be done earlier because pre-build-checks deletes existing databases, and this can't happen if a connection to the database has been opened
            # self.get_database_connection creates the master_database in the desired folder
            self.master_database_conn, self.master_database_cursor = self.get_database_connection(self.master_database_path, self.database_signals.create_database_textbox)
            self.create_db.generate_database(self.master_database_conn, self.master_database_cursor)
        else:
            return
        # close the master database so it can be opened in run_checker (assumption is that create_database isn't always used)
        self.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_path)

    def clear_all_text_boxes(self, text_browsers):
        # Create a list of QTextBrowser widgets by inspecting the module
        for text_browser in text_browsers:
            text_browser.clear()

    def delete_existing_files(self, files):
        for file_name in files:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"Deleted existing file: {file_name}")
    
    def run_checker(self):
        self.current_database_folder = self.ui.checker_data_input_path.text() # path to current database folder
        self.current_database_path = os.path.join(self.current_database_folder, self.current_database_path) # actual path to current database
        # clear all text boxes before running the checker
        self.clear_all_text_boxes(self.text_browsers)
        # delete existing csv files so they can be updated; these files are used to fill tabs and create the pdf report
        self.delete_existing_files(self.report_csv_files)
        self.delete_existing_files(self.csv_mod_files)
        # instantiate run_checker
        self.run_checker = RunChecker(self.current_database_path, self.run_checker_signals.run_checker_textbox, self.current_database_folder)
        
        # FOUR PARTS TO RUN CHECKING
        # before starting confirm pre-build checks; checking whether a valid path was provided for new current database
        path_selected = self.run_checker.pre_build_checks()
        if path_selected:
            # establish database connections; operate under assumption that master_database won't be created each time widget is used
            self.master_database_conn, self.master_database_cursor = self.get_database_connection(self.master_database_path, self.database_signals.create_database_textbox)
            self.current_database_conn, self.current_database_cursor = self.get_database_connection(self.current_database_path, self.database_signals.create_database_textbox)

            # instantiate generate_database and create the current month's database
            self.create_db = BuildDatabase(self.current_database_path, None, self.run_checker_signals.run_checker_textbox, self.current_database_folder, self.raster_target_folder, self.vector_target_folder)
            self.create_db.generate_database(self.current_database_conn, self.current_database_cursor)

            # compliance = East and West tables within each database have the same date and the new current database is at least one month older than the master database
            # required to proceed further
            compliance = self.run_checker.confirm_database_compliance(self.master_database_conn, self.current_database_conn)
            # check compliance; databases are dated correctly and are at least one month apart
            if not compliance:
                utils.show_warning_popup('You have error messages that need to be addressed.  See the Progress Report window.')
            else:
                # PART 1 OF 4 - check the current database and confirm that each sub-folder in the EAST and WEST primary folders contain the chart folders listed in that folder's .csv file
                # e.g., for the RM-ARC folder in the EAST folder, the charts listed in the RM-ARC.csv are in the associated BSBCHART folder
                # note - not needed for the master database; assumption is that this was confirmed in the previous month (the master in month X was the current in month X-1)
                self.check_folder_content = CheckFolderContent(self.master_database_cursor, self.current_database_cursor)
                missing_files, extra_files = self.check_folder_content.check_folders(self.current_database_cursor)
                # report charts_missing
                if missing_files or extra_files:
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                    # Determine which list to pass: missing_files or extra_files
                    # Process missing files if any
                    if missing_files:
                        utils.process_report(missing_files, 'misc_findings_type2', self.errors_signals.errors_textbox, self.current_database_folder)
                    # Process extra files if any
                    if extra_files:
                        utils.process_report(extra_files, 'misc_findings_type2', self.errors_signals.errors_textbox, self.current_database_folder)

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
                            utils.process_report(table_list, 'misc_findings_type2', self.errors_signals.errors_textbox, self.current_database_folder, message)

                # PART 3 OF 4 - compare master and current databases and report charts withdrawn and new charts
                # Remove tables_missing_from_current from tables_master so table content matches; no need to check tables_missing_in_master because these are newly added
                tables_master_temp = [table for table in tables_master_temp if table not in tables_current_temp]
                # instantiate CompareChartNumbers
                self.compare_chart_numbers = CompareChartNumbers(self.master_database_cursor, self.current_database_cursor)
                charts_withdrawn, new_charts = self.compare_chart_numbers.compare_chart_numbers(tables_master_temp, self.master_yyyymmdd, self.current_yyyymmdd)
                # Report missing charts on missing charts tab; can't use same process as above because of filenames and textbox identification
                if charts_withdrawn:
                    utils.process_report(charts_withdrawn, 'charts_withdrawn', self.charts_withdrawn_signals.chart_withdrawn_textbox, self.current_database_folder)
               # Report new charts on new charts tab
                if new_charts:
                    utils.process_report(new_charts, 'new_charts', self.new_charts_signals.new_charts_textbox, self.current_database_folder)
                
               # PART 4 OF 4 - find data mismatches
                # instantiate FindDataMismatches
                self.find_data_mismatches = FindDataMismatches(self.master_database_cursor, self.current_database_cursor)
                new_editions, misc_findings = self.find_data_mismatches.find_mismatches(tables_master_temp, self.master_yyyymmdd, self.current_yyyymmdd)
                # report new_editions
                if new_editions:
                    utils.process_report(new_editions, 'new_editions', self.new_editions_signals.new_editions_textbox, self.current_database_folder)
                # Report misc. findings (findings that couldn't be categorized as New Charts, New Editions or Charts Withdrawn)
                if misc_findings:
                    message = "Uncategorized Findings"
                    utils.process_report(misc_findings, 'misc_findings_type1', self.errors_signals.errors_textbox, self.current_database_folder, message)
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                
                # Print a message to indicate that the checker has run
                self.run_checker_signals.run_checker_textbox.emit('\nThe Checker ran succesfully!')
        else:
            if not path_selected:
                utils.show_warning_popup("The path selected for the current month is invalid.")
            elif self.master_database_path == '':
                utils.show_warning_popup("You need to create a master database before conducting the current month comparison.")
            return
        
        # close the databases
        self.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_path)
        self.close_database(self.run_checker_signals.run_checker_textbox, self.current_database_conn, self.current_database_path)

    def create_pdf_report(self):
        # establish database connections; operate under assumption that master_database won't be created each time widget is used
        self.master_database_conn, self.master_database_cursor = self.get_database_connection(self.master_database_path, self.database_signals.create_database_textbox)
        self.current_database_conn, self.current_database_cursor = self.get_database_connection(self.current_database_path, self.database_signals.create_database_textbox)
        # set report title
        report_title = f"{self.master_yyyymmdd}_VS_{self.current_yyyymmdd} CHS DVD Report"
        # establish the current folder as the folder within which to save the report
        path = os.path.join(self.current_database_folder, f"{report_title}.pdf")   
        # instantiate pdf_report
        self.create_pdf_report = PDFReport(path)
        # Add title to the report
        self.create_pdf_report.add_report_title(report_title)
        # Add toc to the report
        self.create_pdf_report.add_toc('Table of Contents')
        # Filter only the _mod.csv files; formatted csv for gui window and pdf report
        csv_files = glob.glob(self.current_database_folder + "/*_mod.csv") 
        # Create a set of filenames from csv_files for faster lookup
        csv_files_set = set(map(lambda x: x.split('\\')[-1], csv_files))
        # Filter out filenames from csv_files that are not in self.csv_mod_files; possible not all files were created (e.g., no misc findings so no misc files)
        csv_files_filtered = [filename for filename in csv_files_set if filename in self.csv_mod_files]
        # Sort csv_files_filtered to match the order of self.csv_mod_files
        csv_files_sorted = sorted(csv_files_filtered, key=lambda x: self.csv_mod_files.index(x))
        for file in csv_files_sorted:
            csv_file_path = os.path.join(self.current_database_folder, file)
            # Add the content as a table to the PDF report
            self.create_pdf_report.add_table(csv_file_path)
        # Save the report
        self.create_pdf_report.save_report()
        # Print a message to indicate that the checker has run
        self.run_checker_signals.run_checker_textbox.emit('\nThe .pdf report was created succesfully!')
        # close the databases
        self.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_path)
        self.close_database(self.run_checker_signals.run_checker_textbox, self.current_database_conn, self.current_database_path)

def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()

    # using this monospace font (best one I've tried) so text in the pyQT Gui TextBrowser windows is spaced evenly
    font = QFont("Consolas")

    # Get all text browsers from the UI and scroll them to the top and set the font so all columns line-up in gui tabs
    for browser in window.text_browsers:
        browser.verticalScrollBar().minimum()
        browser.setFont(font)
        
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
