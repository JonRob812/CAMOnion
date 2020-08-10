from CAMOnion.ui.camo_position_widget_ui import Ui_Form
from CAMOnion.ui.camo_position_frame_ui import Ui_Frame

from PyQt5.QtWidgets import QFrame, QWidget
from PyQt5 import QtCore as qc


class PositionWidget(QFrame, Ui_Frame, QWidget):
    change_current_origin = qc.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.origin_combo.currentIndexChanged.connect(self.emit_change_origin)

    def emit_change_origin(self):
        self.change_current_origin.emit(self.origin_combo.itemData(self.origin_combo.currentIndex()))

