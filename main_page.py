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

        self.folder_path_list = []

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.folder_path_list.append(folder_path)
            self.populate_file_list(folder_path)
        if len(self.folder_path_list) == 2:
            print(f'2 folders selected -> {self.folder_path_list}')

    def populate_file_list(self, folder_path):
        # Get the list of files in the folder
        try:
            self.select_files_textbox.emit(folder_path)  # Emit the file name directly
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error reading folder: {str(e)}')

    def process_selected_files(self):
        print('processing selected files')

# Main application loop
if __name__ == '__main__':
    pass
