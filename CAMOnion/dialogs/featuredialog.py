from CAMOnion.ui.camo_feature_dialog_ui import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGridLayout


class FeatureDialog(QDialog, Ui_Dialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
        self.frame_layout = QGridLayout(self.frame)
        self.buttonBox.accepted.connect(self.accept)



