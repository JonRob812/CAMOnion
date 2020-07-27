from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5 import QtCore
from CAMOnion.ui.camo_connect_window_ui import Ui_Dialog


class ConnectWindow(QDialog, Ui_Dialog):
    def __init__(self, controller):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.controller = controller
        self.setupUi(self)
        self.user_input.setText(self.controller.db)
        self.buttonBox.accepted.connect(self.set_db)
        self.choose_file_button.clicked.connect(self.show_file_getter)

        self.file_getter = None

    def set_db(self):
        self.controller.db = self.user_input.text()
        self.controller.settings.setValue('db', self.controller.db)
        self.controller.setup_sql()

    def show_file_getter(self):
        path, _ = QFileDialog.getOpenFileName(self, caption='choose camo.db', filter='sqlite.db (*.db)')
        if path:
            self.user_input.setText(path)
            print(path)


class Message(QMessageBox):
    def __init__(self):
        super(QMessageBox, self).__init__()


def show_connect_error():
    msg = Message()
    msg.setWindowTitle('SQL error')
    msg.setText('invalid credentials')
    msg.setIcon(Message.Critical)
    msg.exec_()