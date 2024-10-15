from pathlib import Path
import time
import common_utils as utils
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5.QtCore import QObject, pyqtSignal

class MainPage(QWidget, QObject):
    finished = pyqtSignal(list)  # used to return self.database_path

    def __init__(self, ui, list_widget):
        super().__init__()
        self.ui = ui

        # Create custom_signals connections
        self.list_widget = list_widget  # Reference to listWidgetTextBrowser

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

    # Function to extract the creation month of a folder
    def get_creation_month(self, folder_path):
        folder = Path(folder_path)
        creation_time = folder.stat().st_ctime
        # Convert to a time struct and extract the month (1-12)
        creation_month = time.localtime(creation_time).tm_mon
        return creation_month
    
    def process_selected_files(self):
        print('Processing folders')

        if len(self.folder_path_list) != 2:
            utils.show_warning_popup("Please select two folders. If you made an error, select 'Delete Selected Folders' and start again.")
            return

        # Unpack folder paths
        folder1, folder2 = self.folder_path_list

        # Get creation months for both folders
        month1, month2 = self.get_creation_month(folder1), self.get_creation_month(folder2)

        # Ensure folders are at least one month apart and assign the earlier as master
        if month1 == month2:
            print("Both folders were created in the same month. Selected folders must be at least one month apart. "
                "Select 'Delete Selected Folders' and start again.")
            return

        # Use a conditional expression to determine which is master and which is current
        master_database_path, current_database_path = (folder1, folder2) if month1 < month2 else (folder2, folder1)

        # Emit the result
        self.finished.emit([master_database_path, current_database_path])
       

# Main application loop
if __name__ == '__main__':
    pass
