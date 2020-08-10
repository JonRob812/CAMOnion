from CAMOnion.ui.camo_slot_widget_ui import Ui_Form
from PyQt5.QtWidgets import QWidget


class SlotWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)