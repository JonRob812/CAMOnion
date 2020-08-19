

from PyQt5.QtWidgets import QMessageBox


class ErrorMessage(QMessageBox):
    def __init__(self, title, message, icon=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(message)
        if not icon:
            icon = self.Warning
        self.setIcon(icon)


def show_error_message(title, message, icon=None):
    message = ErrorMessage(title, message, icon)
    message.exec_()

