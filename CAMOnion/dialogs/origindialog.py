from CAMOnion.ui.camo_origin_dialog_ui import Ui_Dialog

from PyQt5.QtWidgets import QDialog


class OriginDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

