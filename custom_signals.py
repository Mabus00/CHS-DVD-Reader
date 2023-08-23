'''
Custom signals and slots module to handle all comms between components.

Custom signals are connected to event handlers.

Organized by tabs in gui.

'''

from PyQt5.QtCore import QObject, pyqtSignal

class CreateDatabaseSignals(QObject):
    # Define custom signals specific to the "Create / Rebuild Database" tab
    rebuild_checkbox_changed = pyqtSignal(bool)

# Define more custom signals for other tabs if needed
