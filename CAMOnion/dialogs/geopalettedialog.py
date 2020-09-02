

from CAMOnion.ui.camo_geo_palette_dialog_ui import Ui_Dialog

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt


class GeoPaletteDialog(QDialog, Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.setupUi(self)
