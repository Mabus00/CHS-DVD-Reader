import os
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal

class MainPage(QWidget, QObject):
    finished = pyqtSignal(list)  # used to return self.database_path

    def __init__(self, ui, master_database_path, current_database_path, select_files_textbox):
        super().__init__()
        self.ui = ui

        self.master_database_path = master_database_path  # actual path to master database
        self.current_database_path = current_database_path  # actual path to current database

        # Create custom_signals connections
        self.select_files_textbox = select_files_textbox

        self.folder_path_list = []

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.folder_path_list.append(folder_path)
            self.populate_file_list(folder_path)
        if len(self.folder_path_list) == 2:
            self.finished.emit(self.folder_path_list)  # Emit the result through the signal

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
