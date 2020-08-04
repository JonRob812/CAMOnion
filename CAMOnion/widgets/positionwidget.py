from CAMOnion.ui.camo_position_widget_ui import Ui_Form

from PyQt5.QtWidgets import QWidget


class PositionWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
