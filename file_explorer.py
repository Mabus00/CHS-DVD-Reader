import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog

class FileExplorerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Explorer")
        self.setGeometry(100, 100, 400, 150)

        self.open_button = QPushButton("Open File", self)
        self.open_button.setGeometry(150, 30, 100, 30)
        self.open_button.clicked.connect(self.open_file_dialog)

        self.file_path_label = QLabel("", self)
        self.file_path_label.setGeometry(20, 80, 360, 30)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            self.file_path_label.setText("Selected File: " + file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorerApp()
    window.show()
    sys.exit(app.exec_())
