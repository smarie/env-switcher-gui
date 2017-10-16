# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/sprint2_dynamic.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(470, 335)
        MainWindow.setWindowTitle("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.envsTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.envsTabWidget.setObjectName("envsTabWidget")
        self.envTab1 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.envTab1.sizePolicy().hasHeightForWidth())
        self.envTab1.setSizePolicy(sizePolicy)
        self.envTab1.setObjectName("envTab1")
        self.envTab1GridLayout = QtWidgets.QGridLayout(self.envTab1)
        self.envTab1GridLayout.setContentsMargins(0, 0, 0, 0)
        self.envTab1GridLayout.setObjectName("envTab1GridLayout")
        self.envTab1FormLayout = QtWidgets.QFormLayout()
        self.envTab1FormLayout.setObjectName("envTab1FormLayout")
        self.var1Label = QtWidgets.QLabel(self.envTab1)
        self.var1Label.setText("env_var_1")
        self.var1Label.setObjectName("var1Label")
        self.envTab1FormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.var1Label)
        self.var1LineEdit = QtWidgets.QLineEdit(self.envTab1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.var1LineEdit.sizePolicy().hasHeightForWidth())
        self.var1LineEdit.setSizePolicy(sizePolicy)
        self.var1LineEdit.setText("env_var_1_value")
        self.var1LineEdit.setObjectName("var1LineEdit")
        self.envTab1FormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.var1LineEdit)
        self.var2Label = QtWidgets.QLabel(self.envTab1)
        self.var2Label.setText("env_var_2")
        self.var2Label.setObjectName("var2Label")
        self.envTab1FormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.var2Label)
        self.var2LineEdit = QtWidgets.QLineEdit(self.envTab1)
        self.var2LineEdit.setText("env_var_2_value")
        self.var2LineEdit.setObjectName("var2LineEdit")
        self.envTab1FormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.var2LineEdit)
        self.envTab1GridLayout.addLayout(self.envTab1FormLayout, 0, 0, 1, 1)
        self.envsTabWidget.addTab(self.envTab1, "Env Name 1")
        self.verticalLayout.addWidget(self.envsTabWidget)
        self.mainButtonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.mainButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.mainButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.mainButtonBox.setObjectName("mainButtonBox")
        self.verticalLayout.addWidget(self.mainButtonBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 470, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.envsTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open..."))
        self.actionOpen.setToolTip(_translate("MainWindow", "Open Configuration File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setToolTip(_translate("MainWindow", "Save Configuration File"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
        self.actionSave_As.setToolTip(_translate("MainWindow", "Save Configuration To Another File"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+F4"))
