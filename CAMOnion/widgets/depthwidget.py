from CAMOnion.ui.depth_widget_ui import Ui_Form
from PyQt5.QtWidgets import QWidget


class DepthWidget(QWidget, Ui_Form):
    def __init__(self, label_text):
        self.label_text = label_text
        super().__init__()
        self.setupUi(self)
        self.depth_label.setText(self.label_text)

