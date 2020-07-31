from PyQt5.QtWidgets import QMainWindow
from CAMOnion.ui.camo_operation_window_ui import Ui_MainWindow


class OperationWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

