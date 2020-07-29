
from PyQt5 import QtWidgets as qw, QtCore as qc


class CamoCADView(qw.QGraphicsView):
    element_selected = qc.pyqtSignal(object, qc.QPointF)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setParent(self.parent)
        self._view_buffer = .2

    def fit_to_scene(self):
        r = self.sceneRect()
        bx, by = r.width() * self._view_buffer / 2, r.height() * self._view_buffer / 2
        self.fitInView(self.sceneRect().adjusted(-bx, -by, bx, by), qc.Qt.KeepAspectRatio)

