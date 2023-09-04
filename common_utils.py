''' 

module of common functions

'''
import os
import sqlite3
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

''' Databse common functions '''

def initialize_database(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    return conn, cursor

def get_database_connection(database_name):
    conn, cursor = initialize_database(database_name)
    return conn, cursor

def delete_existing_database(database_name, text_browser_widget):
    if os.path.exists(database_name):
        os.remove(database_name)
        update_text_browser(text_browser_widget, f"Database '{database_name}' deleted.")

