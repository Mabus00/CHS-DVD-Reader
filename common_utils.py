''' 

module of common functions

'''

from PyQt5.QtWidgets import QMessageBox

def show_warning_popup(message):
    popup = QMessageBox()
    popup.setWindowTitle("Alert")
    popup.setText(message)
    popup.setIcon(QMessageBox.Warning)
    popup.exec_()

def update_text_browser(text_browser, message):
    text_browser.insertPlainText(message + "\n")  # Append the message and a newline
    text_browser.ensureCursorVisible()


