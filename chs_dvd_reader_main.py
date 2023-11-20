'''
Main CONTROLLER for app.  There are two sub controllers:
1. sub-controller to build_database
2. sub-controller to run_checker.

I chose to use custom signals and slots to provide greater seperation of concerns and looser coupling.
I could have gone directly from the UI signal to the slot but chose this instead.
Note that I control almost all signals from here.  I could have done that in utils but i felt if went against the MVC architecture.

tables = CHS DVD folders

Signals are controlled from here only.

VIEW = chs_dvd_gui

'''

import sys
import inspect
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser
from chs_dvd_gui import Ui_MainWindow
from custom_signals import CreateDatabaseSignals, RunCheckerSignals, NewChartsSignals, NewEditionsSignals, WithdrawnSignals, ErrorsSignals
from build_database import BuildDatabase
from run_checker import RunChecker
from compare_databases import CompareDatabases
from compare_chart_numbers import CompareChartNumbers
from find_data_mismatches import FindDataMismatches
import common_utils as utils
from create_pdf_report import PDFReport

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CHS DVD Reader")

        # create list of text browsers so they can be cleared en masse
        self.text_browsers = [obj for name, obj in inspect.getmembers(self.ui) if isinstance(obj, QTextBrowser)]

        # set database connections
        self.master_database_conn = ""
        self.master_database_cursor = ""
        self.current_database_conn = ""
        self.current_database_cursor = ""

        # set master database input path to nothing; user must select path manually 
        self.master_database_input_path = ""
        self.master_database_name = "master_database.db"

        # set current month database input path to nothing; user must select path manually 
        self.current_database_input_path = ""
        self.current_database_name = "current_database.db"

        # create reports list
        self.reports = ["misc_findings.txt"]

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

        # Connect UI signals to custom signals using object names
        # run checker tab
        self.ui.selectCheckerDataPathButton.clicked.connect(self.run_checker_signals.data_input_path_button.emit)
        self.ui.runCheckerButton.clicked.connect(self.run_checker_signals.run_checker_button.emit)
        self.ui.buildNewMasterDatabaseButton.clicked.connect(self.run_checker_signals.build_new_master_database_button.emit)
        self.ui.createPDFReportButton.clicked.connect(self.run_checker_signals.create_pdf_report_button.emit)
        # create database tab
        self.ui.selectDataPathButton.clicked.connect(self.database_signals.database_input_path_button.emit)
        self.ui.buildDatabaseButton.clicked.connect(self.database_signals.build_database_button.emit)

        # Connect custom signals to slots
        # run checker tab
        self.run_checker_signals.data_input_path_button.connect(lambda: utils.open_file_explorer(self.ui.checker_data_input_path, self.current_database_input_path))
        self.run_checker_signals.run_checker_button.connect(self.run_checker)
        self.run_checker_signals.build_new_master_database_button.connect(self.update_master_database)
        self.run_checker_signals.create_pdf_report_button.connect(self.create_pdf_report)
        # create database tab
        self.database_signals.database_input_path_button.connect(lambda: utils.open_file_explorer(self.ui.database_input_path, self.master_database_input_path))
        self.database_signals.build_database_button.connect(self.build_database)

        # Using a lambda function to create an anonymous function that takes a single argument 'message'.
        # The lambda function is being used as an argument to the emit method of the custom signal.
        self.run_checker_signals.run_checker_textbox.connect(lambda message: utils.update_text_browser(self.ui.runCheckerTextBrowser, message))
        self.errors_signals.errors_textbox.connect(lambda message: utils.update_text_browser(self.ui.errorsTextBrowser, message))
        self.new_charts_signals.new_charts_textbox.connect(lambda message: utils.update_text_browser(self.ui.newChartsTextBrowser, message))
        self.new_editions_signals.new_editions_textbox.connect(lambda message: utils.update_text_browser(self.ui.newEditionsTextBrowser, message))
        self.charts_withdrawn_signals.chart_withdrawn_textbox.connect(lambda message: utils.update_text_browser(self.ui.chartsWithdrawnTextBrowser, message))
        self.database_signals.create_database_textbox.connect(lambda message: utils.update_text_browser(self.ui.createDatabaseTextBrowser, message))

        # initial state of run_checker ran successfully flag; needed to confirm the program was run before the master_database can be overwritten
        self.run_checker_successful = False

    def build_database(self):
        # instantiate create_database and pass instance of database_name, etc...
        self.create_db = BuildDatabase(self.master_database_name, self.ui.rebuild_checkbox, self.database_signals.create_database_textbox, self.ui.database_input_path.text())
        # confirm that pre-build checks are met before proceeding        
        if all(self.create_db.pre_build_checks()):
            # establish database connections; operate under assumption that master_database won't be created each time widget is used
            # note that this can't be done earlier because pre-build-checks deletes existing databases, and this can't happen if a connection to the database has been opened
            self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database_name, self.database_signals.create_database_textbox)
            self.create_db.generate_database(self.master_database_conn, self.master_database_cursor, 'Master Database')
        else:
            return
        # close the master database so it can be opened in run_checker (assumption is that create_database isn't always used)
        utils.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_name)

    def run_checker(self):
        # clear all text boxes before running the checker
        utils.clear_all_text_boxes(self.text_browsers)

        # delete existing .txt files so they can be updated; these files are used to fill tabs and create the pdf report
        # first get a list of all files in the current directory
        files = os.listdir()
        # Loop through the files and delete those with a .txt extension
        for file in files:
            if file.endswith('.txt'):
                os.remove(file)
        
        # instantiate run_checker
        self.run_checker = RunChecker(self.current_database_name, self.run_checker_signals.run_checker_textbox, self.ui.checker_data_input_path.text())
        
        # THREE PARTS TO RUN CHECKING
        # before starting confirm pre-build checks (checking whether to delete existing database and a valid path is provided) are met
        if self.run_checker.pre_build_checks():
            # establish database connections; operate under assumption that master_database won't be created each time widget is used
            self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database_name, self.database_signals.create_database_textbox)
            self.current_database_conn, self.current_database_cursor = utils.get_database_connection(self.current_database_name, self.database_signals.create_database_textbox)

            # instantiate generate_database and create the current month's database
            self.create_db = BuildDatabase(self.current_database_name, None, self.run_checker_signals.run_checker_textbox, self.ui.checker_data_input_path.text())
            self.create_db.generate_database(self.current_database_conn, self.current_database_cursor, 'Current Database')

            # compliance = East and West tables within each database have the same date and the new current database is at least one month older than the master database
            # required to proceed further
            compliance = self.run_checker.confirm_database_compliance(self.master_database_conn, self.current_database_conn)
            # check compliance; databases are dated correctly and are at least one month apart
            if not compliance:
                utils.show_warning_popup('You have error messages that need to be addressed.  See the Progress Report window.')
            else:
                # PART 1 OF 3 - compare the folder content of the master and current databases and report new (i.e., not in master but in current) or missing / withdrawn
                # (i.e., in master but not in current) folders on the appropriate tabs.
                # run this first so you can ignore missing tables in PART 2 and 3
                self.compare_databases = CompareDatabases(self.master_database_cursor, self.current_database_cursor)
                # tables_missing_in_current represent tables that have been removed; tables_missing_in_master represent tables that have been added in current
                # tables_master_temp and tables_current_temp have yyyymmdd removed; do this once and share with other modules
                # master_yyyymmdd and current_yyyymmdd are the extracted yyyymmdd for each
                tables_master_temp, tables_missing_in_master, tables_missing_in_current, master_yyyymmdd, current_yyyymmdd = self.compare_databases.compare_databases()
                # report withdrawn or new folders in current_database
                if tables_missing_in_current or tables_missing_in_master:
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                    error_messages = {
                        "missing_current": "Folders removed from this month's DVDs:",
                        "missing_master": "Folders added to this month's DVDs:",
                    }
                    for error_type, table_list in {"missing_current": tables_missing_in_current, "missing_master": tables_missing_in_master}.items():
                        if table_list:
                            message = error_messages[error_type]
                            utils.update_selected_tab(table_list, current_yyyymmdd, self.errors_signals.errors_textbox, message)

                # PART 2 OF 2 - compare master and current databases and report charts withdrawn and new charts
                # Remove tables_missing_from_current from tables_master so table content matches; no need to check tables_missing_in_master because these are newly added
                tables_master_temp = list(set(tables_master_temp) - set(tables_missing_in_current))
                # instantiate CompareChartNumbers
                self.compare_chart_numbers = CompareChartNumbers(self.master_database_cursor, self.current_database_cursor)
                charts_withdrawn, new_charts = self.compare_chart_numbers.compare_chart_numbers(tables_master_temp, master_yyyymmdd, current_yyyymmdd)
                # Report missing charts on missing charts tab; can't use same process as above because of textbox identification
                if charts_withdrawn:
                    message = "Charts missing in current DVD folder"
                    utils.update_new_charts_tab(charts_withdrawn, self.charts_withdrawn_signals.chart_withdrawn_textbox, message)
                # Report new charts on new charts tab
                if new_charts:
                    message = "New charts in current DVD folder"
                    utils.update_new_charts_tab(new_charts, self.new_charts_signals.new_charts_textbox, message)

                # PART 3 OF 3 - find data mismatches
                # instantiate FindDataMismatches
                self.find_data_mismatches = FindDataMismatches(self.master_database_cursor, self.current_database_cursor)
                new_editions, misc_findings = self.find_data_mismatches.find_mismatches(tables_master_temp, master_yyyymmdd, current_yyyymmdd)
                # report new_editions and misc. findings (findings that couldn't be categorized as New Charts, New Editions or Charts Withdrawn)
                # Report missing charts on missing charts tab; can't use same process as above because of textbox identification
                if new_editions:
                    message = "The following folders have new editions:"
                    utils.update_new_editions_tab(new_editions, current_yyyymmdd, self.new_editions_signals.new_editions_textbox, message)
                # Report new charts on new charts tab
                if misc_findings:
                    message = "The following folders have uncategorized findings that may indicate potential errors:"
                    utils.update_selected_tab(misc_findings, current_yyyymmdd, self.errors_signals.errors_textbox, message)
                    utils.show_warning_popup("Possible errors were noted. See the Misc. Results tab.")
                # Print a message to indicate that the checker has run
                self.run_checker_signals.run_checker_textbox.emit('\nThe Checker ran succesfully!')
                self.run_checker_successful = True
        else:
            self.run_checker_successful = False
            return
        
        # close the databases
        utils.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_name)
        utils.close_database(self.run_checker_signals.run_checker_textbox, self.current_database_conn, self.current_database_name)

    def update_master_database(self):
        # first confirm the program has run successfully before allowing user to update the master_database
        if self.run_checker_successful:
            # confirm errors are accepted
            if self.ui.errorsTextBrowser.toPlainText().strip() == "":
                # if no misc_results then nothing to confirm
                self.ui.acceptErrorsCheckBox.setChecked(True)  # Check the acceptErrorsCheckBox (on misc_resutls tab)
                #self.ui.acceptResultsCheckBox.setChecked(True)  # Check the acceptResultsCheckBox (on run_checker tab)
            else:
                print('misc results textbox is NOT empty')
            # both acceptErrorsCheckBox and acceptResultsCheckBox must be checked before proceeding
            if self.ui.acceptErrorsCheckBox.isChecked() and self.ui.acceptResultsCheckBox.isChecked():
                print(f'Accept Misc. Results is {self.ui.acceptErrorsCheckBox.isChecked()}')
                print(f'Results reviewed and acceptable is {self.ui.acceptResultsCheckBox.isChecked()}')
                # confirm with popup
                confirmation = utils.yes_or_no_popup("Are you sure you want to overwrite the Master Database with the current CHS DVDs?")
                if confirmation == 16384: # pyQT code returned for yes
                    print(f'user says yes {confirmation}')
                    utils.delete_existing_database(self.master_database_name, self.run_checker_signals.run_checker_textbox)
                    utils.rename_database(self.current_database_name, self.master_database_name)
                else:
                    print(f'user says no {confirmation}')
            else:
                print('misc_results and/or run_checker results not accepted; returning')
                return
        else:
            print('run_checker hasnt run')
            return

    def create_pdf_report(self):
        print('create_pdf_report')

        # establish database connections; operate under assumption that master_database won't be created each time widget is used
        self.master_database_conn, self.master_database_cursor = utils.get_database_connection(self.master_database_name, self.database_signals.create_database_textbox)
        self.current_database_conn, self.current_database_cursor = utils.get_database_connection(self.current_database_name, self.database_signals.create_database_textbox)

        table_prefixes = ['EastDVD', 'WestDVD']
        master_dates, current_dates = self.run_checker.get_databases_yyyymmdd(self.master_database_conn, self.current_database_conn, table_prefixes)

        # set report title
        report_title = f"{current_dates['EastDVD']} CHS DVD Report"

        # instantiate pdf_report
        self.create_pdf_report = PDFReport(f"{report_title}.pdf")
        
        # Add content to the report
        self.create_pdf_report.add_title(100, 750, report_title)
        self.create_pdf_report.add_paragraph(100, 700, "This is the content of the report.")

        for report in self.reports:
            print(f'reports: {report}')

        
        # Save the report
        self.create_pdf_report.save_report()
        
        # close the databases
        utils.close_database(self.database_signals.create_database_textbox, self.master_database_conn, self.master_database_name)
        utils.close_database(self.run_checker_signals.run_checker_textbox, self.current_database_conn, self.current_database_name)

def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
