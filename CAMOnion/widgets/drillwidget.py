from CAMOnion.ui.camo_drill_widget_ui import Ui_Form
from PyQt5.QtWidgets import QWidget


class DrillWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
