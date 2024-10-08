import os
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QFileDialog, QMessageBox

class MainPage(QWidget):
    def __init__(self, ui, master_database_path, current_database_path, select_files_textbox, progress_textbox, errors_textbox, chart_withdrawn_textbox, new_charts_textbox, new_editions_textbox, master_database_folder, current_database_folder, raster_target_folder, vector_target_folder):
        super().__init__()
        self.ui = ui

        self.master_database_path = master_database_path  # actual path to master database
        self.current_database_path = current_database_path  # actual path to current database

        # Create custom_signals connections
        self.select_files_textbox = select_files_textbox
        self.progress_textbox = progress_textbox

        # Create custom_signals connections
        self.errors_textbox = errors_textbox
        self.chart_withdrawn_textbox = chart_withdrawn_textbox
        self.new_charts_textbox = new_charts_textbox
        self.new_editions_textbox = new_editions_textbox

        # database data input path
        self.master_database_folder = master_database_folder  # path to master database folder
        self.current_database_folder = current_database_folder

        self.raster_target_folder = raster_target_folder
        self.vector_target_folder = vector_target_folder

        self.master_database_conn = ''
        self.master_database_cursor = ''



        # # Set up the layout and widgets
        # self.layout = QVBoxLayout()

        # self.layout.addWidget(self.select_folder_button)

        # self.file_list_widget = QListWidget()
        # self.layout.addWidget(self.file_list_widget)

        # self.setLayout(self.layout)
        # self.setWindowTitle('File Selector')

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.populate_file_list(folder_path)

    def populate_file_list(self, folder_path):
        # Clear existing items
        # self.select_files_textbox.clear()

        # Get the list of files in the folder
        try:
            self.select_files_textbox.emit(folder_path)  # Emit the file name directly
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error reading folder: {str(e)}')

    def process_selected_files(self):
        # Get selected files
        selected_items = self.file_list_widget.selectedItems()
        if selected_items:
            selected_files = [item.text() for item in selected_items]
            QMessageBox.information(self, 'Selected Files', f'Files selected for processing: {", ".join(selected_files)}')
            # Add your file processing logic here
        else:
            QMessageBox.warning(self, 'No Selection', 'No files selected for processing.')

    def run_dvd_checker(self):
        print('running dvd checker')
        self.open_folder_dialog()

# Main application loop
if __name__ == '__main__':
    pass
