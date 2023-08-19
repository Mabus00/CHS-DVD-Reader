'''

Inital pyqt5 module to enable pyqt5 designer

'''

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys

class CHS_DVD_Reader(QMainWindow): # inherit properties and methods from QMainWindow
    def __init__(self): # self is QMainWindow
        # calling constructor of parent class QMainWindow; done to ensure that the initialization code in the parent class is executed before any additional initialization specific to CHS_DVD_Reader is done. It's a common practice to call the parent class constructor using super() in order to properly set up inherited attributes and methods.
        super(CHS_DVD_Reader, self).__init__()
        self.setGeometry(200, 200, 300, 300) #size of window (xpos, ypos, width, height); from left corner of screen
        self.setWindowTitle("CHS DVD Checker")
        self.initUI()

    def initUI(self):
        self.label = QLabel(self) # want the label to appear in the window
        self.label.setText("first label")
        self.label.move(50, 50) # from top left corner of widget window

        self.b1 = QtWidgets.QPushButton(self) # button
        self.b1.setText("Click me")

        self.b1.clicked.connect(self.b1_clicked) # mapping click of button to the function (with the brackets)

    def b1_clicked(self):
        self.label.setText("you pressed the button")
        self.update()

    def update(self): # update size of label to fit text provided
        self.label.adjustSize()

# define the gui window
def window():
    app = QApplication(sys.argv) # config setup; every GUI app must have exactly one instance of QApplication
    win = CHS_DVD_Reader()

    win.show()
    sys.exit(app.exec()) #close window when top right corner 'X' selected

window()