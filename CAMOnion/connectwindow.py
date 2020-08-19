from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5 import QtCore
from CAMOnion.ui.camo_connect_window_ui import Ui_Dialog


class ConnectWindow(QDialog, Ui_Dialog):
    new_db = QtCore.pyqtSignal(str)

    def __init__(self, controller):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.controller = controller
        self.setupUi(self)
        self.user_input.setText(self.controller.db)
        self.buttonBox.accepted.connect(self.set_db)
        self.file_getter = None

    def set_db(self):
        self.new_db.emit(self.user_input.text())



