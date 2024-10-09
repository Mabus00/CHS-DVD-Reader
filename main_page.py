import os
import common_utils as utils
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5.QtCore import QObject, pyqtSignal

class MainPage(QWidget, QObject):
    finished = pyqtSignal(list)  # used to return self.database_path

    def __init__(self, ui, master_database_path, current_database_path, select_files_textbox, list_widget, clear_folders_button):
        super().__init__()
        self.ui = ui

        self.master_database_path = master_database_path  # actual path to master database
        self.current_database_path = current_database_path  # actual path to current database

        # Create custom_signals connections
        self.select_files_textbox = select_files_textbox
        self.list_widget = list_widget  # Reference to listWidgetTextBrowser
        self.clear_folders_button = clear_folders_button

        self.folder_path_list = []

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.folder_path_list.append(folder_path)
        print(len(self.folder_path_list))
        if folder_path and len(self.folder_path_list) < 3:
            self.populate_file_list(folder_path)
        elif folder_path and len(self.folder_path_list) > 2:
            utils.show_warning_popup("Only two folders are allowed. If you made an error select 'Delete Selected Folders' and start again.")
            self.folder_path_list.pop()

    def populate_file_list(self, folder_path):
        # Get the list of files in the folder
        try:
            # This method will handle adding items to the QListWidget
            item = QListWidgetItem(folder_path)  # Create a QListWidgetItem from the message
            self.list_widget.addItem(item)  # Add the item to the QListWidget
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error reading folder: {str(e)}')

    def clear_list_widget_textbox(self):
        # Get the list of files in the folder
        try:
            self.list_widget.clear()  # Use the reference to clear the QListWidget
            self.folder_path_list = []
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error reading folder: {str(e)}')

    def process_selected_files(self):
        print('processing selected files')
        self.finished.emit(self.folder_path_list)  # Emit the result through the signal

# Main application loop
if __name__ == '__main__':
    pass
