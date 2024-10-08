import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QMessageBox

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout and widgets
        self.layout = QVBoxLayout()

        self.select_folder_button = QPushButton('Select Folder')
        self.select_folder_button.clicked.connect(self.open_folder_dialog)
        self.layout.addWidget(self.select_folder_button)

        self.file_list_widget = QListWidget()
        self.layout.addWidget(self.file_list_widget)

        self.process_button = QPushButton('Process Selected Files')
        self.process_button.clicked.connect(self.process_selected_files)
        self.layout.addWidget(self.process_button)

        self.setLayout(self.layout)
        self.setWindowTitle('File Selector')

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.populate_file_list(folder_path)

    def populate_file_list(self, folder_path):
        # Clear existing items
        self.file_list_widget.clear()

        # Get the list of files in the folder
        try:
            files = os.listdir(folder_path)
            for file in files:
                # Add file to QListWidget
                self.file_list_widget.addItem(file)
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

# Main application loop
if __name__ == '__main__':
    pass
