from CAMOnion.ui.camo_face_widget_ui import Ui_Form
from PyQt5.QtWidgets import QWidget


class FaceWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
