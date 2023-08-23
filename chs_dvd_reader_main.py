import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up UI components
        self.setWindowTitle("CHS DVD Reader")  # Set the window title

              # Create an instance of CreateDatabaseSignals
        self.create_database_signals = CreateDatabaseSignals()

        # Connect rebuild_checkbox's stateChanged signal to emit the custom signal
        self.ui.rebuild_checkbox.stateChanged.connect(self.emit_rebuild_checkbox_status)

        # ... other setup ...

    def emit_rebuild_checkbox_status(self, state):
        # Emit the custom signal with the checkbox status (True or False)
        self.create_database_signals.rebuild_checkbox_changed.emit(state)
        print(f"Rebuild checkbox state changed: {state}")


def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
