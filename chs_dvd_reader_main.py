''' add comments'''


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
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

        print(f"Build Database Button pressed")


def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
