'''
Main CONTROLLER for app.  There are two sub controllers:
1. sub-controller to build_database
2. sub-controller to run_checker.

I chose to use custom signals and slots to provide greater seperation of concerns and looser coupling.
I could have gone directly from the UI signal to the slot but chose this instead.

tables = CHS DVD folders

Signals are controlled from here only.

VIEW = chs_dvd_gui

'''

import sys
import os
import inspect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals, RunCheckerSignals, NewChartsSignals, WithdrawnSignals, ErrorsSignals
from build_database import BuildDatabase
from run_checker import RunChecker
from compare_databases import CompareDatabases
from compare_chart_numbers import CompareChartNumbers
import common_utils as utils

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # create list of text browsers so they can be cleared en masse
        self.text_browsers = [obj for name, obj in inspect.getmembers(self.ui) if isinstance(obj, QTextBrowser)]

        # set master database input path to nothing; user must select path manually 
        self.master_database_input_path = ""
        self.master_database_name = "chs_dvd.db"

        # set current month database input path to nothing; user must select path manually 
        self.current_database_input_path = ""
        self.current_database_name = "current_month.db"

        # Create an instance of RunCheckerSignals
        self.run_checker_signals = RunCheckerSignals()

        # Create an instance of NewChartsSignals
        self.new_charts_signals = NewChartsSignals()

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
        # create database tab
        self.ui.selectDataPathButton.clicked.connect(self.database_signals.database_input_path_button.emit)
        self.ui.buildDatabaseButton.clicked.connect(self.database_signals.build_database_button.emit)

        # Connect custom signals to slots
        # run checker tab
        self.run_checker_signals.data_input_path_button.connect(lambda: utils.open_file_explorer(self.ui.checker_data_input_path, self.current_database_input_path))
        self.run_checker_signals.run_checker_button.connect(self.run_checker)

        # create database tab
        self.database_signals.database_input_path_button.connect(lambda: utils.open_file_explorer(self.ui.database_input_path, self.master_database_input_path))
        self.database_signals.build_database_button.connect(self.build_database)

        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.run_checker_signals.run_checker_textbox.connect(lambda message: utils.update_text_browser(self.ui.runCheckerTextBrowser, message))
        self.errors_signals.errors_textbox.connect(lambda message: utils.update_text_browser(self.ui.errorsTextBrowser, message))
        self.new_charts_signals.new_charts_textbox.connect(lambda message: utils.update_text_browser(self.ui.newChartsTextBrowser, message))
        self.charts_withdrawn_signals.chart_withdrawn_textbox.connect(lambda message: utils.update_text_browser(self.ui.chartsWithdrawnTextBrowser, message))
        self.database_signals.create_database_textbox.connect(lambda message: utils.update_text_browser(self.ui.createDatabaseTextBrowser, message))

    def build_database(self):
        # instantiate create_database and pass instance of database_name, etc...
        self.create_db = BuildDatabase(self.master_database_name, self.ui.rebuild_checkbox, self.database_signals.create_database_textbox, self.ui.database_input_path.text())
        # confirm that pre-conditions are met before proceeding        
        if all(self.create_db.pre_build_checks()):
            # establish database connections; operate under assumption that master_database won't be created each time widget is used
            master_database_conn, master_database_cursor = utils.get_database_connection(self.master_database_name, self.database_signals.create_database_textbox)
            self.create_db.generate_database(master_database_conn, master_database_cursor)
        else:
            return
        # close the master database so it can be opened in run_checker (assumption is that create_database isn't always used)
        utils.close_database(self.database_signals.create_database_textbox, master_database_conn, self.master_database_name)

    def run_checker(self):
        # clear all text boxes before running the checker
        utils.clear_all_text_boxes(self.text_browsers)

        # delete if necessary then build new current database
        # NOTE UNCOMMENT FOR PRODUCTION ONLY
        if os.path.exists(self.current_database_name):
            utils.delete_existing_database(self.current_database_name, self.run_checker_signals.run_checker_textbox)

        # establish database connections; operate under assumption that master_database won't be created each time widget is used
        master_database_conn, master_database_cursor = utils.get_database_connection(self.master_database_name, self.database_signals.create_database_textbox)
        current_database_conn, current_database_cursor = utils.get_database_connection(self.current_database_name, self.database_signals.create_database_textbox)

        # ensure user has selected a current data input path
        if not utils.confirm_data_path(self.ui.checker_data_input_path.text()):
            return

        # create current database
        # instantiate generate_database and pass instance of database_signals to create the current month's database; note rebuild_checkbox not needed
        # NOTE UNCOMMENT FOR PRODUCTION ONLY
        self.create_db = BuildDatabase(self.current_database_name, None, self.run_checker_signals.run_checker_textbox, self.ui.checker_data_input_path.text())
        self.create_db.generate_database(current_database_conn, current_database_cursor)

        # instantiate run_checker
        self.run_checker = RunChecker(self.run_checker_signals.run_checker_textbox, self.errors_signals.errors_textbox, master_database_conn, current_database_conn)
        # compliance = East and West tables within each database have the same date and the new current database is at least one month older than the master database
        # required to proceed further
        compliance = self.run_checker.confirm_database_compliance()
        # check compliance
        if not compliance:
            utils.show_warning_popup('You have error messages that need to be ackowledged before proceeding.')
        else:
            # Compares the content of the master and current databases and finds new (i.e., not in master but in current) or missing 
            # (i.e., in master but not in current) tables and reports the findings on the error tab
            # need to run this first so you can ignore missing tables in follow on code
            self.compare_databases = CompareDatabases(self.run_checker_signals.run_checker_textbox, self.errors_signals.errors_textbox, master_database_cursor, current_database_cursor)
            # tables_missing_in_current represent tables that have been removed, whereas tables_missing_in_master represent tables that have been added
            # tables_master_temp and tables_current_temp have yyyymmdd removed; do this once and share with other modules
            # master_yyyymmdd and current_yyyymmdd are the extracted yyyymmdd for each; do this once and share with other modules
            tables_master_temp, tables_current_temp, tables_missing_in_master, tables_missing_in_current, master_yyyymmdd, current_yyyymmdd = self.compare_databases.compare_databases()

            # Remove tables_missing_from_current from tables_master so table content matching can occur; no need to check tables_missing_in_master because these are newly added
            tables_master_temp = [table for table in tables_master_temp if table not in tables_missing_in_current]

            # creates instance of CompareChartNumbers
            self.compare_databases = CompareChartNumbers(master_database_cursor, current_database_cursor)
            # compares master and current databases and report charts withdrawn; which database is compared to which is controlled by the order of the yyyymmdd
            charts_withdrawn, new_charts = self.compare_databases.compare_chart_numbers(tables_master_temp, master_yyyymmdd, current_yyyymmdd)

            # Print missing charts
            if charts_withdrawn:
                for table_name, missing_charts in charts_withdrawn:
                    self.charts_withdrawn_signals.chart_withdrawn_textbox.emit(f"Charts missing in current DVD folder {table_name}:")
                    # Concatenate the missing chart names with commas and print them
                    missing_chart_str = ', '.join(missing_charts)
                    self.charts_withdrawn_signals.chart_withdrawn_textbox.emit(missing_chart_str + '\n')
                
            # Print new charts
            if new_charts:
                for table_name, missing_charts in new_charts:
                    self.new_charts_signals.new_charts_textbox.emit(f"New charts in current DVD folder {table_name}:")
                    # Concatenate the missing chart names with commas and print them
                    missing_chart_str = ', '.join(missing_charts)
                    self.new_charts_signals.new_charts_textbox.emit(missing_chart_str + '\n')
                

            # Compares master and current databases and report new charts


        # for now; TODO add checkboxes so user can indicate errors are acceptable / not acceptable
        # required signal before the master database is rebuilt using the current database
        print(f'accept errors is {self.ui.acceptErrorsCheckBox.isChecked()}')
        
        # 7. add the ability to print the result as a pdf.
        # 8. once all has been verified and the user is happy, overwrite the master with the current.

        # Print a message to indicate that the checker has run
        print('The Checker ran succesfully!')

        # close the master database so it can be opened in run_checker (assumption is that create_database isn't always used)
        utils.close_database(self.database_signals.create_database_textbox, master_database_conn, self.master_database_name)
        utils.close_database(self.run_checker_signals.run_checker_textbox, current_database_conn, self.current_database_name)

def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
