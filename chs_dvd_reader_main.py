'''
Main controller for app.

Note I chose to use custom signals and slots to provide greater seperation of concerns and looser coupli.g
I could have gone directly from the UI signal to the slot but chose this instead.

'''

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals
from create_database import CreateDatabase
import common_utils as utils

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # set default database input path to nothing; user must select path manually 
        self.default_database_input_path = ""
        self.database_name = "chs_dvd.db"

        # establish database connections for various tabs
        create_database_conn, create_database_cursor = utils.get_database_connection(self.database_name)

        # Create an instance of CreateDatabaseSignals
        self.database_signals = CreateDatabaseSignals()

        # create and pass instance of database_signals to CreateDatabase so it can use the create_rebuild_database_textbox
        self.create_db = CreateDatabase(self.database_signals)

        # Connect UI signals to custom signals using object names
        self.ui.buildDatabaseButton.clicked.connect(self.database_signals.build_database_button.emit)
        self.ui.selectDataPathButton.clicked.connect(self.database_signals.data_input_path_button.emit)

        # Connect custom signals to slots
        self.database_signals.build_database_button.connect(self.build_database)
        self.database_signals.data_input_path_button.connect(self.open_file_explorer)
        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.database_signals.create_database_textbox.connect(lambda message: self.update_text_browser(self.ui.rebuildDatabaseTextBrowser, message))

    def update_text_browser(self, text_browser, message):
        text_browser.insertPlainText(message + "\n")  # Append the message and a newline
        text_browser.ensureCursorVisible()

    def build_database(self):
        # builds database
        if os.path.exists(self.database_name):
            # chs_dvd.db exists
            if not self.ui.rebuild_checkbox.isChecked():
                utils.show_warning_popup("Database exists. Check the 'Confirm deletion of database' box to proceed")
                return
            utils.delete_existing_database(self.database_name, self.ui.rebuildDatabaseTextBrowser)

        # ensure user has selected a data input path
        if not os.path.exists(self.default_database_input_path):
            utils.show_warning_popup("Select data input path")
            return
                
        # passing self.ui.rebuildDatabaseTextBrowser as the text_browser_widget I want the message sent to
        self.create_db.open_database(self.database_name, self.ui.rebuildDatabaseTextBrowser)
        self.create_db.build_database(self.default_database_input_path, self.ui.rebuildDatabaseTextBrowser)

    def open_file_explorer(self):
        self.default_database_input_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.default_database_input_path = self.default_database_input_path.replace("/", "\\")
        self.ui.data_input_path.setText(self.default_database_input_path)


def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
