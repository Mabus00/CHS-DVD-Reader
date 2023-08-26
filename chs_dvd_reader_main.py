''' '''


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals
from create_database import CreateDatabase

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up UI components
        self.setWindowTitle("CHS DVD Reader")  # Set the window title

        self.create_db = CreateDatabase()

        # Create an instance of CreateDatabaseSignals
        self.create_database_signals = CreateDatabaseSignals()

        # Connect the custom signal to a slot to delete the database
        self.ui.rebuild_checkbox.stateChanged.connect(self.emit_rebuild_checkbox_status)

        self.ui.buildDatabaseButton.clicked.connect(self.delete_database_if_checked)

        # Connect the custom signal to a slot to open the file explorer
        self.ui.selectDataPathButton.clicked.connect(self.open_file_explorer)

    def emit_rebuild_checkbox_status(self, state):
        # Emit the custom signal with the checkbox status (True or False)
        self.create_database_signals.rebuild_checkbox_changed.emit(state)
        print(f"Rebuild checkbox state changed: {state}")

    def delete_database_if_checked(self):
        print('here')
        if self.ui.rebuild_checkbox.isChecked():
            print('checked')
            # Create an instance of CreateDatabase and call delete_existing_database
            self.create_db.delete_existing_database()

            #self.create_db.open_database()

        print(f"Build Database Button pressed")

    def open_file_explorer(self):
        self.data_input_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if self.data_input_path:
            self.ui.data_input_path.setText(self.data_input_path)
            print(f"Selected Folder Path: {self.data_input_path}")


def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
