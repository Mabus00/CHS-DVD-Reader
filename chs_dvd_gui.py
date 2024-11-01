# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CHS_DVD_Checker.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(250, 10, 351, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(30, 70, 781, 471))
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
        self.runCheckerButton.setGeometry(QtCore.QRect(20, 130, 301, 41))
        self.runCheckerButton.setObjectName("runCheckerButton")
        self.runCheckerProgressReportLabel = QtWidgets.QLabel(self.checker)
        self.runCheckerProgressReportLabel.setGeometry(QtCore.QRect(20, 210, 171, 21))
        self.runCheckerProgressReportLabel.setObjectName("runCheckerProgressReportLabel")
        self.runCheckerTextBrowser = QtWidgets.QTextBrowser(self.checker)
        self.runCheckerTextBrowser.setGeometry(QtCore.QRect(20, 250, 601, 151))
        self.runCheckerTextBrowser.setObjectName("runCheckerTextBrowser")
        self.tabWidget.addTab(self.checker, "")
        self.new_charts = QtWidgets.QWidget()
        self.new_charts.setObjectName("new_charts")
        self.newChartsLabel = QtWidgets.QLabel(self.new_charts)
        self.newChartsLabel.setGeometry(QtCore.QRect(20, 40, 391, 61))
        self.newChartsLabel.setObjectName("newChartsLabel")
        self.newChartsTextBrowser = QtWidgets.QTextBrowser(self.new_charts)
        self.newChartsTextBrowser.setGeometry(QtCore.QRect(20, 100, 601, 221))
        self.newChartsTextBrowser.setObjectName("newChartsTextBrowser")
        self.tabWidget.addTab(self.new_charts, "")
        self.new_editions = QtWidgets.QWidget()
        self.new_editions.setObjectName("new_editions")
        self.newEditionsTextBrowser = QtWidgets.QTextBrowser(self.new_editions)
        self.newEditionsTextBrowser.setGeometry(QtCore.QRect(20, 100, 601, 221))
        self.newEditionsTextBrowser.setObjectName("newEditionsTextBrowser")
        self.newChartsLabel_2 = QtWidgets.QLabel(self.new_editions)
        self.newChartsLabel_2.setGeometry(QtCore.QRect(20, 40, 391, 61))
        self.newChartsLabel_2.setObjectName("newChartsLabel_2")
        self.tabWidget.addTab(self.new_editions, "")
        self.withdrawals = QtWidgets.QWidget()
        self.withdrawals.setObjectName("withdrawals")
        self.chartsWithdrawnTextBrowser = QtWidgets.QTextBrowser(self.withdrawals)
        self.chartsWithdrawnTextBrowser.setGeometry(QtCore.QRect(20, 100, 601, 221))
        self.chartsWithdrawnTextBrowser.setObjectName("chartsWithdrawnTextBrowser")
        self.newChartsLabel_3 = QtWidgets.QLabel(self.withdrawals)
        self.newChartsLabel_3.setGeometry(QtCore.QRect(20, 40, 391, 61))
        self.newChartsLabel_3.setObjectName("newChartsLabel_3")
        self.tabWidget.addTab(self.withdrawals, "")
        self.errors = QtWidgets.QWidget()
        self.errors.setObjectName("errors")
        self.errorsTextBrowser = QtWidgets.QTextBrowser(self.errors)
        self.errorsTextBrowser.setGeometry(QtCore.QRect(20, 100, 601, 221))
        self.errorsTextBrowser.setObjectName("errorsTextBrowser")
        self.newChartsLabel_4 = QtWidgets.QLabel(self.errors)
        self.newChartsLabel_4.setGeometry(QtCore.QRect(20, 40, 391, 61))
        self.newChartsLabel_4.setObjectName("newChartsLabel_4")
        self.acceptErrorsCheckBox = QtWidgets.QCheckBox(self.errors)
        self.acceptErrorsCheckBox.setGeometry(QtCore.QRect(20, 360, 351, 21))
        self.acceptErrorsCheckBox.setObjectName("acceptErrorsCheckBox")
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
        self.createDatabaseTextBrowser = QtWidgets.QTextBrowser(self.rebuild_database)
        self.createDatabaseTextBrowser.setGeometry(QtCore.QRect(20, 250, 601, 151))
        self.createDatabaseTextBrowser.setObjectName("createDatabaseTextBrowser")
        self.tabWidget.addTab(self.rebuild_database, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 21))
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
        self.tabWidget.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "CHS MONTHLY DVD CHECKER"))
        self.selectCheckerDataPathButton.setText(_translate("MainWindow", "Press to select input data path"))
        self.runCheckerButton.setText(_translate("MainWindow", "Run CHS DVD Checker Program"))
        self.runCheckerProgressReportLabel.setText(_translate("MainWindow", "Progress Report:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.checker), _translate("MainWindow", "Run Checker"))
        self.newChartsLabel.setText(_translate("MainWindow", "The following New Charts are announced:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.new_charts), _translate("MainWindow", "New Charts"))
        self.newChartsLabel_2.setText(_translate("MainWindow", "The following New Editions are announced:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.new_editions), _translate("MainWindow", "New Editions"))
        self.newChartsLabel_3.setText(_translate("MainWindow", "The following charts are announced as withdrawn:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.withdrawals), _translate("MainWindow", "Charts Withdrawn"))
        self.newChartsLabel_4.setText(_translate("MainWindow", "The following errors were detected:"))
        self.acceptErrorsCheckBox.setText(_translate("MainWindow", "The above errors are acceptable "))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.errors), _translate("MainWindow", "Errors"))
        self.rebuild_checkbox.setText(_translate("MainWindow", "Check to confirm: delete and rebuild database?"))
        self.createDatabaseProgressReportLabel.setText(_translate("MainWindow", "Progress Report:"))
        self.buildDatabaseButton.setText(_translate("MainWindow", "Execute Create Database"))
        self.selectDataPathButton.setText(_translate("MainWindow", "Press to select input data path"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rebuild_database), _translate("MainWindow", "Create Master Database"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "Save as new database"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
