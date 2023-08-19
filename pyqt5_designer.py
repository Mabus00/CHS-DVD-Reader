'''

Inital pyqt5 module to enable pyqt5 designer

'''

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys

# define the gui window
def window():
    app = QApplication(sys.argv) # config setup; every GUI app must have exactly one instance of QApplication
    win = QMainWindow()
    win.setGeometry(200, 200, 300, 300) #size of window (xpos, ypos, width, height); from left corner of screen
    win.setWindowTitle("CHS DVD Checker")

    label = QLabel(win)
    label.setText("first label")
    label.move(50, 50) # from top left corner

    win.show()
    sys.exit(app.exec())

window()