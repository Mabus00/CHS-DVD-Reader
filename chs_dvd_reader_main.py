'''
Main CONTROLLER for app.  There are three sub controllers:
1. sub-controller to build_database
2. sub-controller to run_checker.
3. sub-controller to build pdf report.

I chose to use custom signals and slots to provide greater seperation of concerns and looser coupling.
I could have gone directly from the UI signal to the slot but chose this instead.
Note that I control almost all signals from here.  I could have done that in utils but i felt if went against the MVC architecture.

tables = CHS DVD folders

Signals are controlled from here only.

VIEW = chs_dvd_gui

'''

import sys
import inspect
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from chs_dvd_gui import Ui_MainWindow
from custom_signals import MainPageSignals, CreateDatabaseSignals, RunCheckerSignals, NewChartsSignals, NewEditionsSignals, WithdrawnSignals, ErrorsSignals
from main_page import MainPage
from build_database import BuildDatabase
from run_checker import RunChecker
from create_pdf_report import CreatePDFReport

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # create list of text browsers so they can be cleared en masse
        self.text_browsers = [obj for name, obj in inspect.getmembers(self.ui) if isinstance(obj, QTextEdit)]

        # create an ordered list of csv files so I can prioritize selection for the pdf report
        self.report_csv_files = [
            "misc_findings_type1.csv",
            "misc_findings_type2.csv",
            "new_editions.csv",
            "new_charts.csv",
            "charts_withdrawn.csv"
        ]
        
        # these files are pre-formatted versions of the above files; used for the gui windows and pdf report
        self.csv_mod_files = [
            "misc_findings_type1_mod.csv",
            "misc_findings_type2_mod.csv",
            "new_editions_mod.csv",
            "new_charts_mod.csv",
            "charts_withdrawn_mod.csv"
        ]

        # set database connections
        self.master_database_conn = ""
        self.master_database_cursor = ""
        self.current_database_conn = ""
        self.current_database_cursor = ""

        self.master_yyyymmdd = ""
        self.current_yyyymmdd = ""

        # set master database input path to nothing; user must select path manually 
        self.master_database_path = ""
        self.master_database = "master_database.db"

        # set current month database input path to nothing; user must select path manually 
        self.current_database_path = ""
        self.current_database = "current_database.db"

        # target folders to find to process data
        self.raster_target_folder = 'BSBCHART'
        self.vector_target_folder = 'ENC_ROOT'

        # Create an instance of MainPageSignals 
        self.main_page_signals = MainPageSignals()

        # Create an instance of RunCheckerSignals 
        self.run_checker_signals = RunCheckerSignals()

        # Create an instance of NewChartsSignals
        self.new_charts_signals = NewChartsSignals()

        # Create an instance of NewChartsSignals
        self.new_editions_signals = NewEditionsSignals()

        # Create an instance of ErrorsSignals
        self.errors_signals = ErrorsSignals()

        # Create an instance of WithdrawnSignals
        self.charts_withdrawn_signals = WithdrawnSignals()

        # Create an instance of CreateDatabaseSignals
        self.database_signals = CreateDatabaseSignals()

        # Create an instance of BuildDatabase
        self.main_page_instance = MainPage(self.ui, self.ui.listWidgetTextBrowser, self.main_page_signals.progress_textbox)
          
        # Create an instance of BuildDatabase
        self.build_database_instance = BuildDatabase(self.ui, self.main_page_signals.progress_textbox, self.raster_target_folder, self.vector_target_folder)
        
        # Create an instance of RunChecker
        self.run_checker_instance = RunChecker(self.ui, self.main_page_signals.progress_textbox, self.errors_signals.errors_textbox, self.charts_withdrawn_signals.chart_withdrawn_textbox, self.new_charts_signals.new_charts_textbox, self.new_editions_signals.new_editions_textbox, self.raster_target_folder, self.vector_target_folder)

        # Create an instance of CreatePDFReport
        self.create_pdf_report_instance = CreatePDFReport(self.run_checker_signals.run_checker_textbox)

        # Connect UI signals to custom signals using object names
        # main page tab
        self.ui.selectFoldersButton.clicked.connect(self.main_page_signals.select_folders_button.emit)
        self.ui.deleteSelectedFoldersButton.clicked.connect(self.main_page_signals.clear_folders_button.emit)
        self.ui.executeCheckerButton.clicked.connect(self.main_page_signals.run_dvd_checker_button.emit)

        # Connect custom signals to slots
        # main page tab
        self.main_page_signals.select_folders_button.connect(lambda: self.main_page_instance.open_folder_dialog())
        self.main_page_signals.clear_folders_button.connect(lambda: self.main_page_instance.clear_list_widget_textbox())
        self.main_page_signals.run_dvd_checker_button.connect(lambda: self.main_page_instance.process_selected_files())
        # Connect the finished signal to handle_build_database_result
        self.main_page_instance.finished.connect(self.handle_main_page_result, Qt.QueuedConnection)

        # Connect the finished signal to handle_build_database_result
        self.run_checker_instance.finished.connect(self.handle_run_checker_result, Qt.QueuedConnection)
        # create_pdf_report custom signal
        # self.run_checker_signals.create_pdf_report_button.connect(lambda: self.create_pdf_report_instance.create_pdf_report())

        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.main_page_signals.progress_textbox.connect(lambda message: self.update_text_browser(self.ui.mainPageTextBrowser, message))
        self.errors_signals.errors_textbox.connect(lambda message: self.update_text_browser(self.ui.errorsTextBrowser, message))
        self.new_charts_signals.new_charts_textbox.connect(lambda message: self.update_text_browser(self.ui.newChartsTextBrowser, message))
        self.new_editions_signals.new_editions_textbox.connect(lambda message: self.update_text_browser(self.ui.newEditionsTextBrowser, message))
        self.charts_withdrawn_signals.chart_withdrawn_textbox.connect(lambda message: self.update_text_browser(self.ui.chartsWithdrawnTextBrowser, message))

    def open_file_explorer(self, parent, input_path):
        input_path = QFileDialog.getExistingDirectory(parent, "Select Folder")
        input_path = input_path.replace("/", "\\")
        parent.setText(input_path)

    def update_text_browser(self, text_browser, message):
        # updates the selected text_browser with a simple message
        text_browser.insertPlainText(message + "\n")  # Append the message and a newline
        text_browser.ensureCursorVisible()
    
    def clear_all_text_boxes(self, text_browsers):
        # Create a list of QTextBrowser widgets by inspecting the module
        for text_browser in text_browsers:
            text_browser.clear()

    def handle_run_checker_result(self, master_yyyymmdd, current_yyyymmdd):
        self.create_pdf_report_instance.update_paths(master_yyyymmdd, current_yyyymmdd, self.current_database_path)

    def handle_main_page_result(self, master_database_path, current_database_path):
        self.master_database_path = master_database_path
        self.current_database_path = current_database_path
        self.build_database_instance.build_database(self.master_database, self.master_database_path)
        self.run_checker_instance.run_checker(self.master_database, self.master_database_path, self.current_database, self.current_database_path)
        print(f'selected folders')
        
def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()

    # using this monospace font (best one I've tried) so text in the pyQT Gui TextBrowser windows is spaced evenly
    font = QFont("Consolas")

    # Get all text browsers from the UI and scroll them to the top and set the font so all columns line-up in gui tabs
    for browser in window.text_browsers:
        browser.verticalScrollBar().minimum()
        browser.setFont(font)

    # clear all text boxes before running the checker
    window.clear_all_text_boxes(window.text_browsers)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
