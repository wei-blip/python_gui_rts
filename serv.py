# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/rts/tmp/main_window/serv.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayout.addWidget(self.listWidget)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.helpField = QtWidgets.QTextEdit(self.centralwidget)
        self.helpField.setReadOnly(True)
        self.helpField.setObjectName("helpField")
        self.verticalLayout_2.addWidget(self.helpField)
        self.socketPort = QtWidgets.QLineEdit(self.centralwidget)
        self.socketPort.setObjectName("socketPort")
        self.verticalLayout_2.addWidget(self.socketPort)
        self.choiceMessage = QtWidgets.QComboBox(self.centralwidget)
        self.choiceMessage.setCurrentText("")
        self.choiceMessage.setObjectName("choiceMessage")
        self.verticalLayout_2.addWidget(self.choiceMessage)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.createMessage = QtWidgets.QPushButton(self.centralwidget)
        self.createMessage.setObjectName("createMessage")
        self.verticalLayout.addWidget(self.createMessage)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Server"))
        self.helpField.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Create your message</span></p></body></html>"))
        self.socketPort.setPlaceholderText(_translate("MainWindow", "Socket port"))
        self.createMessage.setText(_translate("MainWindow", "Create message"))
