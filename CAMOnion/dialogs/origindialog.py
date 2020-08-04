from CAMOnion.ui.camo_origin_dialog_ui import Ui_Dialog

from PyQt5.QtWidgets import QDialog
import PyQt5.QtCore


class OriginDialog(QDialog, Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self, None, PyQt5.QtCore.Qt.WindowStaysOnTopHint)
        Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.x_entity = None
        self.y_entity = None

