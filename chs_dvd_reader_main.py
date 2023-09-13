'''
Main controller for app.

Note I chose to use custom signals and slots to provide greater seperation of concerns and looser coupli.g
I could have gone directly from the UI signal to the slot but chose this instead.

'''

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals, RunCheckerSignals
from create_database import CreateDatabase
from run_checker import RunChecker
import common_utils as utils

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # set default database input path to nothing; user must select path manually 
        self.database_input_path = ""
        self.database_name = "chs_dvd.db"

        # set default run chekcer input path to nothing; user must select path manually 
        self.checker_data_input_path = ""
        self.checker_database_name = "current_month.db"

        # Create an instance of RunCheckerSignals
        self.run_checker_signals = RunCheckerSignals()

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
        self.run_checker_signals.data_input_path_button.connect(lambda: utils.open_file_explorer(self.ui.checker_data_input_path, self.checker_data_input_path))
        self.run_checker_signals.run_checker_button.connect(self.run_checker)

        # create database tab
        self.database_signals.database_input_path_button.connect(lambda: utils.open_file_explorer(self.ui.database_input_path, self.database_input_path))
        self.database_signals.build_database_button.connect(self.build_database)

        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.database_signals.create_database_textbox.connect(lambda message: utils.update_text_browser(self.ui.createDatabaseTextBrowser, message))
        self.run_checker_signals.run_checker_textbox.connect(lambda message: utils.update_text_browser(self.ui.runCheckerTextBrowser, message))

    def build_database(self):
        # delete if necessary then build new database
        if os.path.exists(self.database_name):
            # chs_dvd.db exists
            if not self.ui.rebuild_checkbox.isChecked():
                utils.show_warning_popup("Database exists. Check the 'Confirm deletion of database' box to proceed")
                return
            utils.delete_existing_database(self.database_name, self.ui.createDatabaseTextBrowser)

        # ensure user has selected a data input path
        if not self.ui.database_input_path.text():
            utils.show_warning_popup("Select data input path")
            return
        
        # establish database connections for the create/rebuild database tab
        self.create_database_conn, self.create_database_cursor = utils.get_database_connection(self.database_name, self.ui.createDatabaseTextBrowser)

        # instantiate create_database and pass instance of database_signals, database path, database connection and cursor to CreateDatabase
        self.create_db = CreateDatabase(self.database_signals, self.ui.database_input_path.text(), self.create_database_conn, self.create_database_cursor)
        self.create_db.generate_database(self.ui.createDatabaseTextBrowser)

        utils.close_database(self.ui.createDatabaseTextBrowser, self.create_database_conn)

    def run_checker(self):

        # ensure user has selected a data input path
        if not self.ui.checker_data_input_path.text():
            utils.show_warning_popup("Select data input path")
            return
        
        # establish new current database connections for the run checker database tab
        self.run_checker_conn, self.run_checker_cursor = utils.get_database_connection(self.checker_database_name, self.ui.runCheckerTextBrowser)

        # instantiate generate_database and pass instance of database_signals to create the current month's database
        self.create_db = CreateDatabase(self.run_checker_signals, self.ui.checker_data_input_path.text(), self.run_checker_conn, self.run_checker_cursor)
        self.create_db.generate_database(self.ui.runCheckerTextBrowser)

        # instantiate run_checker and pass instance of database_signals, database path, database connection and cursor to RunChecker
        self.run_checker = RunChecker(self.run_checker_signals, self.ui.checker_data_input_path.text(), self.run_checker_conn, self.run_checker_cursor)
        self.run_checker.compare_databases(self.ui.runCheckerTextBrowser)


def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
