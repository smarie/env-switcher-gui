import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QTabWidget, QPushButton

from envswitch.qt_design import Ui_MainWindow


class EnvSwitcherApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # use super to access variables, methods etc in the qt_design.py file
        super(self.__class__, self).__init__()

        # use generated method from qt_design.py to set up layout and widgets that are defined
        self.setupUi(self)

        # connect buttons to events
        self.okCancelApplyButtonBox.accepted.connect(self.accepted)

        # TODO Load last known configuration template


        # TODO Load last known state (= active tab id) ? otherwise not for now.


        # Show
        self.show()

    def accepted(self):
        """ """
        print('accepted_callback_works')

# class MainApp(QMainWindow, Ui_MainWindow):
#     """
#     Main window, that contains the Table Widget - itself containing the tabs
#     """
#
#     def __init__(self):
#         super().__init__()
#         self.title = 'PyQt5 tabs - pythonspot.com'
#         self.left = 100
#         self.top = 100
#         self.width = 500
#         self.height = 400
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#
#         self.table_widget = MyTableWidget(self)
#         self.setCentralWidget(self.table_widget)
#
#         self.show()
#
# class MyTableWidget(QWidget):
#     """
#     The widget that contains the tabs
#     """
#     def __init__(self, parent):
#         super(QWidget, self).__init__(parent)
#         self.layout = QVBoxLayout(self)
#
#         # Initialize tab screen
#         self.tabs = QTabWidget()
#         self.tabs.resize(parent.width, parent.height)
#
#         # Add tabs
#         self.tab1 = QWidget()
#         self.tabs.addTab(self.tab1, "Env 1")
#         self.tab2 = QWidget()
#         self.tabs.addTab(self.tab2, "Env 2")
#         self.tab2 = QWidget()
#         self.tabs.addTab(self.tab2, "Env 3")
#
#         # Create first tab
#         self.tab1.layout = QVBoxLayout(self)
#         self.pushButton1 = QPushButton("PyQt5 button")
#         self.tab1.layout.addWidget(self.pushButton1)
#         self.tab1.setLayout(self.tab1.layout)
#
#         # Add tabs to the layout of widget
#         self.layout.addWidget(self.tabs)
#         self.setLayout(self.layout)
#
#     @pyqtSlot()
#     def on_click(self):
#         print("\n")
#         for currentQTableWidgetItem in self.tableWidget.selectedItems():
#             print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


def main():
    # create the application (the frame around everything), passing in the possible commandline arguments
    app = QApplication(sys.argv)
    # create the main window
    form = EnvSwitcherApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
