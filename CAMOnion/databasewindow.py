from PyQt5 import QtWidgets as qw

from CAMOnion.ui.camo_database_window_ui import Ui_databaseWindow


class databaseWindow(qw.QMainWindow, Ui_databaseWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
