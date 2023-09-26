'''
Main controller for app.

Note I chose to use custom signals and slots to provide greater seperation of concerns and looser coupli.g
I could have gone directly from the UI signal to the slot but chose this instead.

'''

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals, RunCheckerSignals, ErrorsSignals
from create_database import CreateDatabase
from run_checker import RunChecker
from compare_database_content import CompareDatabases
import common_utils as utils

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # set master database input path to nothing; user must select path manually 
        self.master_database_input_path = ""
        self.master_database_name = "chs_dvd.db"

        # set current month database input path to nothing; user must select path manually 
        self.current_database_input_path = ""
        self.current_database_name = "current_month.db"

        # Create an instance of RunCheckerSignals
        self.run_checker_signals = RunCheckerSignals()

        # Create an instance of ErrorsSignals
        self.errors_signals = ErrorsSignals()

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
        self.database_signals.create_database_textbox.connect(lambda message: utils.update_text_browser(self.ui.createDatabaseTextBrowser, message))

    def build_database(self):
        # delete if necessary then build new database
        if os.path.exists(self.master_database_name):
            if not utils.confirm_database_deletion(self.ui.rebuild_checkbox, self.master_database_name, self.ui.createDatabaseTextBrowser):
                return
        
        # ensure user has selected a data input path
        if not utils.confirm_data_path(self.ui.database_input_path.text()):
            return

        # create master database
        # establish database connections; operate under assumption that master_database won't be created each time widget is used
        self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database_name, self.ui.createDatabaseTextBrowser)

        # instantiate create_database and pass instance of database_signals, etc...
        self.create_db = CreateDatabase(self.database_signals.create_database_textbox, self.ui.database_input_path.text(), self.master_database_conn, self.master_database_cursor)
        self.create_db.generate_database()

        # close the master database so it can be opened in run_checker (assumption is that create_database isn't always used)
        utils.close_database(self.ui.createDatabaseTextBrowser, self.master_database_conn, self.master_database_name)

    def run_checker(self):
        # delete if necessary then build new current database
        # NOTE UNCOMMENT FOR PRODUCTION ONLY
        # if os.path.exists(self.master_database_name):
        #     utils.delete_existing_database(self.current_database_name, self.ui.runCheckerTextBrowser)

        # establish database connections; operate under assumption that master_database won't be created each time widget is used
        self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database_name, self.ui.createDatabaseTextBrowser)
        self.current_database_conn, self.current_database_cursor = utils.get_database_connection(self.current_database_name, self.ui.runCheckerTextBrowser)

        # ensure user has selected a current data input path
        if not utils.confirm_data_path(self.ui.checker_data_input_path.text()):
            return

        # create current database
        # instantiate generate_database and pass instance of database_signals to create the current month's database
        # NOTE UNCOMMENT FOR PRODUCTION ONLY
        # self.create_db = CreateDatabase(self.run_checker_signals.run_checker_textbox, self.ui.checker_data_input_path.text(), self.current_database_conn, self.current_database_cursor)
        # self.create_db.generate_database()

        # instantiate run_checker and pass instance of database_signals, etc...
        self.run_checker = RunChecker(self.run_checker_signals.run_checker_textbox, self.errors_signals.errors_textbox, self.master_database_conn, self.current_database_conn)
        compliance = self.run_checker.confirm_database_compliance()

        if not compliance:
            print('not in compliance. program stops here')
        else:
            self.compare_databases = CompareDatabases(self.run_checker_signals.run_checker_textbox, self.errors_signals.errors_textbox, self.master_database_cursor, self.current_database_cursor)
            self.compare_databases.compare_database_content()
            print(compliance)
        # 3. start with master and find the same table (with the newer date) in current
        # self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.
        # 7. add the ability to print the result as a pdf.
        # 8. once all has been verified and the user is happy, overwrite the master with the current.

        # Print a message to indicate that the checker has run
        print('The Checker ran succesfully!')

        # close the master database so it can be opened in run_checker (assumption is that create_database isn't always used)
        utils.close_database(self.ui.createDatabaseTextBrowser, self.master_database_conn, self.master_database_name)
        utils.close_database(self.ui.runCheckerTextBrowser, self.current_database_conn, self.current_database_name)

def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
