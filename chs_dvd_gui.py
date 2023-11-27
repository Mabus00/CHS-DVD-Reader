# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CHS_DVD_Checker.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1129, 862)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(380, 10, 351, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(40, 60, 981, 741))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget.setFont(font)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setObjectName("tabWidget")
        self.checker = QtWidgets.QWidget()
        self.checker.setObjectName("checker")
        self.selectCheckerDataPathButton = QtWidgets.QPushButton(self.checker)
        self.selectCheckerDataPathButton.setGeometry(QtCore.QRect(20, 40, 231, 41))
        self.selectCheckerDataPathButton.setObjectName("selectCheckerDataPathButton")
        self.checker_data_input_path = QtWidgets.QLabel(self.checker)
        self.checker_data_input_path.setGeometry(QtCore.QRect(260, 40, 431, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checker_data_input_path.sizePolicy().hasHeightForWidth())
        self.checker_data_input_path.setSizePolicy(sizePolicy)
        self.checker_data_input_path.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.checker_data_input_path.setText("")
        self.checker_data_input_path.setObjectName("checker_data_input_path")
        self.runCheckerButton = QtWidgets.QPushButton(self.checker)
        self.runCheckerButton.setGeometry(QtCore.QRect(20, 110, 301, 41))
        self.runCheckerButton.setObjectName("runCheckerButton")
        self.runCheckerProgressReportLabel = QtWidgets.QLabel(self.checker)
        self.runCheckerProgressReportLabel.setGeometry(QtCore.QRect(20, 180, 171, 21))
        self.runCheckerProgressReportLabel.setObjectName("runCheckerProgressReportLabel")
        self.runCheckerTextBrowser = QtWidgets.QTextEdit(self.checker)
        self.runCheckerTextBrowser.setGeometry(QtCore.QRect(20, 220, 901, 311))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.runCheckerTextBrowser.setFont(font)
        self.runCheckerTextBrowser.setObjectName("runCheckerTextBrowser")
        self.acceptResultsCheckBox = QtWidgets.QCheckBox(self.checker)
        self.acceptResultsCheckBox.setGeometry(QtCore.QRect(20, 560, 451, 21))
        self.acceptResultsCheckBox.setObjectName("acceptResultsCheckBox")
        self.buildNewMasterDatabaseButton = QtWidgets.QPushButton(self.checker)
        self.buildNewMasterDatabaseButton.setGeometry(QtCore.QRect(20, 600, 201, 41))
        self.buildNewMasterDatabaseButton.setObjectName("buildNewMasterDatabaseButton")
        self.buildNewMasterDatabaseButtonlabel = QtWidgets.QLabel(self.checker)
        self.buildNewMasterDatabaseButtonlabel.setGeometry(QtCore.QRect(230, 610, 571, 21))
        self.buildNewMasterDatabaseButtonlabel.setObjectName("buildNewMasterDatabaseButtonlabel")
        self.createPDFReportButton = QtWidgets.QPushButton(self.checker)
        self.createPDFReportButton.setGeometry(QtCore.QRect(20, 660, 201, 41))
        self.createPDFReportButton.setObjectName("createPDFReportButton")
        self.create_pdf_report_text = QtWidgets.QLabel(self.checker)
        self.create_pdf_report_text.setGeometry(QtCore.QRect(230, 670, 571, 21))
        self.create_pdf_report_text.setObjectName("create_pdf_report_text")
        self.tabWidget.addTab(self.checker, "")
        self.new_charts = QtWidgets.QWidget()
        self.new_charts.setObjectName("new_charts")
        self.newChartsLabel = QtWidgets.QLabel(self.new_charts)
        self.newChartsLabel.setGeometry(QtCore.QRect(20, 10, 391, 61))
        self.newChartsLabel.setObjectName("newChartsLabel")
        self.newChartsTextBrowser = QtWidgets.QTextEdit(self.new_charts)
        self.newChartsTextBrowser.setGeometry(QtCore.QRect(20, 70, 901, 591))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.newChartsTextBrowser.setFont(font)
        self.newChartsTextBrowser.setObjectName("newChartsTextBrowser")
        self.tabWidget.addTab(self.new_charts, "")
        self.new_editions = QtWidgets.QWidget()
        self.new_editions.setObjectName("new_editions")
        self.newChartsLabel_2 = QtWidgets.QLabel(self.new_editions)
        self.newChartsLabel_2.setGeometry(QtCore.QRect(20, 10, 391, 61))
        self.newChartsLabel_2.setObjectName("newChartsLabel_2")
        self.newEditionsTextBrowser = QtWidgets.QTextEdit(self.new_editions)
        self.newEditionsTextBrowser.setGeometry(QtCore.QRect(20, 70, 901, 591))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.newEditionsTextBrowser.setFont(font)
        self.newEditionsTextBrowser.setObjectName("newEditionsTextBrowser")
        self.tabWidget.addTab(self.new_editions, "")
        self.withdrawals = QtWidgets.QWidget()
        self.withdrawals.setObjectName("withdrawals")
        self.newChartsLabel_3 = QtWidgets.QLabel(self.withdrawals)
        self.newChartsLabel_3.setGeometry(QtCore.QRect(20, 10, 391, 61))
        self.newChartsLabel_3.setObjectName("newChartsLabel_3")
        self.chartsWithdrawnTextBrowser = QtWidgets.QTextEdit(self.withdrawals)
        self.chartsWithdrawnTextBrowser.setGeometry(QtCore.QRect(20, 70, 901, 591))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.chartsWithdrawnTextBrowser.setFont(font)
        self.chartsWithdrawnTextBrowser.setObjectName("chartsWithdrawnTextBrowser")
        self.tabWidget.addTab(self.withdrawals, "")
        self.errors = QtWidgets.QWidget()
        self.errors.setObjectName("errors")
        self.newChartsLabel_4 = QtWidgets.QLabel(self.errors)
        self.newChartsLabel_4.setGeometry(QtCore.QRect(20, 10, 391, 61))
        self.newChartsLabel_4.setObjectName("newChartsLabel_4")
        self.acceptErrorsCheckBox = QtWidgets.QCheckBox(self.errors)
        self.acceptErrorsCheckBox.setGeometry(QtCore.QRect(20, 660, 451, 21))
        self.acceptErrorsCheckBox.setObjectName("acceptErrorsCheckBox")
        self.errorsTextBrowser = QtWidgets.QTextEdit(self.errors)
        self.errorsTextBrowser.setGeometry(QtCore.QRect(20, 70, 901, 561))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.errorsTextBrowser.setFont(font)
        self.errorsTextBrowser.setObjectName("errorsTextBrowser")
        self.tabWidget.addTab(self.errors, "")
        self.rebuild_database = QtWidgets.QWidget()
        self.rebuild_database.setObjectName("rebuild_database")
        self.rebuild_checkbox = QtWidgets.QCheckBox(self.rebuild_database)
        self.rebuild_checkbox.setGeometry(QtCore.QRect(20, 20, 361, 31))
        self.rebuild_checkbox.setObjectName("rebuild_checkbox")
        self.createDatabaseProgressReportLabel = QtWidgets.QLabel(self.rebuild_database)
        self.createDatabaseProgressReportLabel.setGeometry(QtCore.QRect(20, 210, 171, 21))
        self.createDatabaseProgressReportLabel.setObjectName("createDatabaseProgressReportLabel")
        self.buildDatabaseButton = QtWidgets.QPushButton(self.rebuild_database)
        self.buildDatabaseButton.setGeometry(QtCore.QRect(20, 140, 301, 41))
        self.buildDatabaseButton.setObjectName("buildDatabaseButton")
        self.selectDataPathButton = QtWidgets.QPushButton(self.rebuild_database)
        self.selectDataPathButton.setGeometry(QtCore.QRect(20, 80, 231, 41))
        self.selectDataPathButton.setObjectName("selectDataPathButton")
        self.database_input_path = QtWidgets.QLabel(self.rebuild_database)
        self.database_input_path.setGeometry(QtCore.QRect(260, 80, 431, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.database_input_path.sizePolicy().hasHeightForWidth())
        self.database_input_path.setSizePolicy(sizePolicy)
        self.database_input_path.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.database_input_path.setText("")
        self.database_input_path.setObjectName("database_input_path")
        self.createDatabaseTextBrowser = QtWidgets.QTextEdit(self.rebuild_database)
        self.createDatabaseTextBrowser.setGeometry(QtCore.QRect(20, 240, 881, 251))
        font = QtGui.QFont()
        font.setFamily("Algerian")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.createDatabaseTextBrowser.setFont(font)
        self.createDatabaseTextBrowser.setObjectName("createDatabaseTextBrowser")
        self.tabWidget.addTab(self.rebuild_database, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1129, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "CHS MONTHLY DVD CHECKER"))
        self.selectCheckerDataPathButton.setText(_translate("MainWindow", "Press to select input data path"))
        self.runCheckerButton.setText(_translate("MainWindow", "Run CHS DVD Checker Program"))
        self.runCheckerProgressReportLabel.setText(_translate("MainWindow", "Progress Report:"))
        self.acceptResultsCheckBox.setText(_translate("MainWindow", "All results have been reviewed and are acceptable"))
        self.buildNewMasterDatabaseButton.setText(_translate("MainWindow", "Update Master Database"))
        self.buildNewMasterDatabaseButtonlabel.setText(_translate("MainWindow", "Selecting this button will make this month\'s database the new Master Database"))
        self.createPDFReportButton.setText(_translate("MainWindow", "Create PDF Report"))
        self.create_pdf_report_text.setText(_translate("MainWindow", "Select this button to create a pdf report for the current month"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.checker), _translate("MainWindow", "Run Checker"))
        self.newChartsLabel.setText(_translate("MainWindow", "The following New Charts are announced:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.new_charts), _translate("MainWindow", "New Charts"))
        self.newChartsLabel_2.setText(_translate("MainWindow", "The following New Editions are announced:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.new_editions), _translate("MainWindow", "New Editions"))
        self.newChartsLabel_3.setText(_translate("MainWindow", "The following charts are announced as withdrawn:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.withdrawals), _translate("MainWindow", "Charts Withdrawn"))
        self.newChartsLabel_4.setText(_translate("MainWindow", "The following results could not be categorized:"))
        self.acceptErrorsCheckBox.setText(_translate("MainWindow", "The above results have been reviewed and are acceptable"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.errors), _translate("MainWindow", "Misc. Findings"))
        self.rebuild_checkbox.setText(_translate("MainWindow", "Check to confirm: delete and rebuild database?"))
        self.createDatabaseProgressReportLabel.setText(_translate("MainWindow", "Progress Report:"))
        self.buildDatabaseButton.setText(_translate("MainWindow", "Execute Create Database"))
        self.selectDataPathButton.setText(_translate("MainWindow", "Press to select input data path"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rebuild_database), _translate("MainWindow", "Create Master Database"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "Save as new database"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
