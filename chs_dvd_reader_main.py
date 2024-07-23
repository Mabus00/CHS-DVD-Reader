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
import os
import common_utils as utils
import glob
import inspect

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog
from PyQt5.QtGui import QFont
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals, RunCheckerSignals, NewChartsSignals, NewEditionsSignals, WithdrawnSignals, ErrorsSignals
from build_database import BuildDatabase
from run_checker import RunChecker
from create_pdf_report import PDFReport

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
        self.master_database_folder = ""
        self.master_database_path = "master_database.db"

        # set current month database input path to nothing; user must select path manually 
        self.current_database_folder = ""
        self.current_database_path = "current_database.db"

        # target folders to find to process data
        self.raster_target_folder = 'BSBCHART'
        self.vector_target_folder = 'ENC_ROOT'

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

        # Instantiate BuildDatabase
        self.build_database_instance = BuildDatabase(self.ui, self.master_database_path, self.database_signals.create_database_textbox, self.master_database_folder, self.raster_target_folder, self.vector_target_folder)
        
        # Instantiate RunChecker
        self.run_checker_instance = RunChecker(self.ui, self.master_database_path, self.current_database_path, self.run_checker_signals.run_checker_textbox, self.errors_signals.errors_textbox, self.database_signals.create_database_textbox, self.charts_withdrawn_signals.chart_withdrawn_textbox, self.new_charts_signals.new_charts_textbox, self.new_editions_signals.new_editions_textbox, self.master_database_folder, self.current_database_folder, self.raster_target_folder, self.vector_target_folder)

        # Connect UI signals to custom signals using object names
        # run checker tab
        self.ui.selectCheckerDataPathButton.clicked.connect(self.run_checker_signals.data_input_path_button.emit)
        self.ui.runCheckerButton.clicked.connect(self.run_checker_signals.run_checker_button.emit)
        self.ui.createPDFReportButton.clicked.connect(self.run_checker_signals.create_pdf_report_button.emit)
        # create database tab
        self.ui.selectDataPathButton.clicked.connect(self.database_signals.database_input_path_button.emit)
        self.ui.buildDatabaseButton.clicked.connect(self.database_signals.build_database_button.emit)

        # Connect custom signals to slots
        # run checker tab
        self.run_checker_signals.data_input_path_button.connect(lambda: self.open_file_explorer(self.ui.checker_data_input_path, self.current_database_path))
        self.run_checker_signals.run_checker_button.connect(self.run_checker_instance.run_checker(self.master_database_path))
        # Connect the finished signal to handle_run_checker_result
        # self.self.run_checker_instance.finished.connect(self.handle_run_checker_result)
        self.run_checker_signals.create_pdf_report_button.connect(self.create_pdf_report)

        # create database tab
        self.database_signals.database_input_path_button.connect(lambda: self.open_file_explorer(self.ui.database_input_path, self.master_database_folder))
        self.database_signals.build_database_button.connect(self.build_database_instance.build_database)
        # Connect the finished signal to handle_build_database_result
        self.build_database_instance.finished.connect(self.handle_build_database_result)

        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.run_checker_signals.run_checker_textbox.connect(lambda message: self.update_text_browser(self.ui.runCheckerTextBrowser, message))
        self.errors_signals.errors_textbox.connect(lambda message: self.update_text_browser(self.ui.errorsTextBrowser, message))
        self.new_charts_signals.new_charts_textbox.connect(lambda message: self.update_text_browser(self.ui.newChartsTextBrowser, message))
        self.new_editions_signals.new_editions_textbox.connect(lambda message: self.update_text_browser(self.ui.newEditionsTextBrowser, message))
        self.charts_withdrawn_signals.chart_withdrawn_textbox.connect(lambda message: self.update_text_browser(self.ui.chartsWithdrawnTextBrowser, message))
        self.database_signals.create_database_textbox.connect(lambda message: self.update_text_browser(self.ui.createDatabaseTextBrowser, message))

    def open_file_explorer(self, parent, input_path):
        input_path = QFileDialog.getExistingDirectory(parent, "Select Folder")
        input_path = input_path.replace("/", "\\")
        parent.setText(input_path)

    def update_text_browser(self, text_browser, message):
        # updates the selected text_browser with a simple message
        text_browser.insertPlainText(message + "\n")  # Append the message and a newline
        text_browser.ensureCursorVisible()

    def handle_build_database_result(self, result):
        self.master_database_path = result

    def clear_all_text_boxes(self, text_browsers):
        # Create a list of QTextBrowser widgets by inspecting the module
        for text_browser in text_browsers:
            text_browser.clear()

    # def handle_run_che_result(self, result):
    #     self.master_database_path = result

    def create_pdf_report(self):
        # establish database connections; operate under assumption that master_database won't be created each time widget is used
        self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database_path, self.database_signals.create_database_textbox)
        self.current_database_conn, self.current_database_cursor = utils.get_database_connection(self.current_database_path, self.database_signals.create_database_textbox)
        # set report title
        report_title = f"{self.master_yyyymmdd}_VS_{self.current_yyyymmdd} CHS DVD Report"
        # establish the current folder as the folder within which to save the report
        path = os.path.join(self.current_database_folder, f"{report_title}.pdf")   
        # instantiate pdf_report
        self.create_pdf_report = PDFReport(path)
        # Add title to the report
        self.create_pdf_report.add_report_title(report_title)
        # Add toc to the report
        self.create_pdf_report.add_toc('Table of Contents')
        # Filter only the _mod.csv files; formatted csv for gui window and pdf report
        csv_files = glob.glob(self.current_database_folder + "/*_mod.csv") 
        # Create a set of filenames from csv_files for faster lookup
        csv_files_set = set(map(lambda x: x.split('\\')[-1], csv_files))
        # Filter out filenames from csv_files that are not in self.csv_mod_files; possible not all files were created (e.g., no misc findings so no misc files)
        csv_files_filtered = [filename for filename in csv_files_set if filename in self.csv_mod_files]
        # Sort csv_files_filtered to match the order of self.csv_mod_files
        csv_files_sorted = sorted(csv_files_filtered, key=lambda x: self.csv_mod_files.index(x))
        for file in csv_files_sorted:
            csv_file_path = os.path.join(self.current_database_folder, file)
            # Add the content as a table to the PDF report
            self.create_pdf_report.add_table(csv_file_path)
        # Save the report
        self.create_pdf_report.save_report()
        # Print a message to indicate that the checker has run
        self.run_checker_signals.run_checker_textbox.emit('\nThe .pdf report was created succesfully!')
        # close the databases
        utils.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_path)
        utils.close_database(self.run_checker_signals.run_checker_textbox, self.current_database_conn, self.current_database_path)

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
