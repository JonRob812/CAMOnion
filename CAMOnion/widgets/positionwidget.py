from CAMOnion.ui.camo_position_widget_ui import Ui_Form
from CAMOnion.ui.camo_position_frame_ui import Ui_Frame

from PyQt5.QtWidgets import QFrame


class PositionWidget(QFrame, Ui_Frame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
