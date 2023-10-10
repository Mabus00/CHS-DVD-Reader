'''
Custom signals and slots (callbacks) module to handle all comms between components.

Custom signals are connected to event handlers.

Organized by tabs in gui.
   
'''

from PyQt5.QtCore import QObject, pyqtSignal

class RunCheckerSignals(QObject):
    # Custom signals specific to the "Run Checker" tab
    data_input_path_button = pyqtSignal()
    run_checker_button = pyqtSignal()
    run_checker_textbox = pyqtSignal(str)

class NewChartsSignals(QObject):
    # Custom signals specific to the "New Chart" tab
    new_charts_textbox = pyqtSignal(str)
    #accept_new_charts_checkbox = pyqtSignal(bool)

class NewEditionsSignals(QObject):
    # Custom signals specific to the "New Edition" tab
    new_edition_detected = pyqtSignal(str)
    edition_verification_failed = pyqtSignal(str)
    new_editions_textbox = pyqtSignal(str)

class WithdrawnSignals(QObject):
    # Custom signals specific to the "Withdrawals" tab
    chart_withdrawn_textbox = pyqtSignal(str)

class ErrorsSignals(QObject):
    # Custom signals specific to the "Errors" tab
    errors_textbox = pyqtSignal(str)
    accept_errors_checkbox = pyqtSignal(bool)

class CreateDatabaseSignals(QObject):
    # Custom signals specific to the "Create / Rebuild Database" tab
    rebuild_checkbox = pyqtSignal(bool)
    build_database_button = pyqtSignal()
    database_input_path_button = pyqtSignal()
    create_database_textbox = pyqtSignal(str)

# Define more custom signals for other tabs if needed
