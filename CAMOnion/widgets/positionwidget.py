from CAMOnion.ui.camo_position_widget_ui import Ui_Form
from CAMOnion.ui.camo_position_frame_ui import Ui_Frame
from CAMOnion.core.widget_tools import get_combo_data

from PyQt5.QtWidgets import QFrame, QWidget
from PyQt5 import QtCore as qc


class PositionWidget(QFrame, Ui_Frame, QWidget):
    change_current_origin = qc.pyqtSignal(object)
    change_active_setup = qc.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.origin_combo.currentIndexChanged.connect(self.emit_change_origin)
        self.active_setup_combo.currentIndexChanged.connect(self.emit_change_active_setup)

    def emit_change_origin(self):
        self.change_current_origin.emit(get_combo_data(self.origin_combo))

    def emit_change_active_setup(self):
        self.change_active_setup.emit(get_combo_data(self.active_setup_combo))

