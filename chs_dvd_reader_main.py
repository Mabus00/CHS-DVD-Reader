'''
Main controller for app.

Note I chose to use custom signals and slots to provide greater seperation of concerns and looser coupli.g
I could have gone directly from the UI signal to the slot but chose this instead.

'''

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals
from create_database import CreateDatabase

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        self.data_input_path = ""
        self.create_db = CreateDatabase()

        # Create an instance of CreateDatabaseSignals
        self.database_signals = CreateDatabaseSignals()

        # Connect UI signals to custom signals using object names
        self.ui.buildDatabaseButton.clicked.connect(self.database_signals.build_database_button.emit)
        self.ui.selectDataPathButton.clicked.connect(self.database_signals.data_input_path_button.emit)

        # Connect custom signals to slots
        self.database_signals.build_database_button.connect(self.build_database)
        self.database_signals.data_input_path_button.connect(self.open_file_explorer)

    def build_database(self):
        if self.ui.rebuild_checkbox.isChecked():
            print('checked')
            #self.create_db.delete_existing_database()

        print(f"Build Database Button pressed")
        if self.data_input_path:
            #self.create_db.process_disks(self.data_input_path)
            print(f"Selected Folder Path: {self.data_input_path}")
        else:
            print("Please select a data input path")

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
