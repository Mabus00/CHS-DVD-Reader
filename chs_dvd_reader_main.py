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
from common_utils import show_warning_popup

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        self.data_input_path = "D:\\"
        self.database_path = "chs_dvd.db"

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
        if os.path.exists(self.database_path):
            # chs_dvd.db exists
            if not self.ui.rebuild_checkbox.isChecked():
                show_warning_popup("Database exists. Check the 'Confirm deletion of database' box to proceed")
                return
            self.create_db.delete_existing_database(self.ui.rebuildDatabaseTextBrowser)
        
        # passing self.ui.rebuildDatabaseTextBrowser as the text_browser_widget I want the message sent to
        self.create_db.open_database(self.ui.rebuildDatabaseTextBrowser)
        self.create_db.process_disks(self.data_input_path, self.ui.rebuildDatabaseTextBrowser)

    def open_file_explorer(self):
        self.data_input_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if self.data_input_path:
            self.ui.data_input_path.setText(self.data_input_path)

def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
