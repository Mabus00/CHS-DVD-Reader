import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from chs_dvd_gui import Ui_MainWindow

class CHSDVDReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up UI components
        self.setWindowTitle("CHS DVD Reader")  # Set the window title

def main():
    app = QApplication(sys.argv)
    window = CHSDVDReaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
