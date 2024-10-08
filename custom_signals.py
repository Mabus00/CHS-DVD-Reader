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
    # Custom signals to replace new database from the current database
    accept_results_checkbox = pyqtSignal(bool)
    build_new_master_database_button = pyqtSignal()
    # Custom siganl to create pdf report
    create_pdf_report_button = pyqtSignal()

class NewChartsSignals(QObject):
    # Custom signals specific to the "New Chart" tab
    new_charts_textbox = pyqtSignal(str)

class NewEditionsSignals(QObject):
    # Custom signals specific to the "New Edition" tab
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

class MainPageSignals(QObject):
    # Custom signals specific to the "Main Page" tab
    run_dvd_checker_button = pyqtSignal()
    select_folders_button = pyqtSignal()
    progress_textbox = pyqtSignal(str)
    select_files_textbox = pyqtSignal(str)