import argparse
import signal
import sys
from functools import partial
from typing import Optional
from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import _get_x_scale, PyQtBackend, CorrespondingDXFEntity, \
    CorrespondingDXFEntityStack
from ezdxf.drawing import Drawing


# class CADGraphicsView(QGraphicsView):
#     def __init__(self, parent=None):
#         super(CADGraphicsView, self).__init__(parent)


class CADGraphicsView(qw.QGraphicsView):
    def __init__(self, view_buffer: float = 0.2):
        super().__init__()
        self._zoom = 1
        self._default_zoom = 1
        self._zoom_limits = (0.5, 100)
        self._view_buffer = view_buffer

        self.setTransformationAnchor(qw.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(qw.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.setDragMode(qw.QGraphicsView.ScrollHandDrag)
        self.setFrameShape(qw.QFrame.NoFrame)
        self.setRenderHints(qg.QPainter.Antialiasing | qg.QPainter.TextAntialiasing | qg.QPainter.SmoothPixmapTransform)

    def clear(self):
        pass

    def fit_to_scene(self):
        r = self.sceneRect()
        bx, by = r.width() * self._view_buffer / 2, r.height() * self._view_buffer / 2
        self.fitInView(self.sceneRect().adjusted(-bx, -by, bx, by), qc.Qt.KeepAspectRatio)
        self._default_zoom = _get_x_scale(self.transform())
        self._zoom = 1

    def _get_zoom_amount(self) -> float:
        return _get_x_scale(self.transform()) / self._default_zoom

    def wheelEvent(self, event: qg.QWheelEvent) -> None:
        # dividing by 120 gets number of notches on a typical scroll wheel. See QWheelEvent documentation
        delta_notches = event.angleDelta().y() / 120
        zoom_per_scroll_notch = 0.2
        factor = 1 + zoom_per_scroll_notch * delta_notches
        resulting_zoom = self._zoom * factor
        if resulting_zoom < self._zoom_limits[0]:
            factor = self._zoom_limits[0] / self._zoom
        elif resulting_zoom > self._zoom_limits[1]:
            factor = self._zoom_limits[1] / self._zoom
        self.scale(factor, factor)
        self._zoom *= factor


class CADGraphicsViewWithOverlay(CADGraphicsView):
    element_selected = qc.pyqtSignal(object, qc.QPointF)

    def __init__(self, parent=None):
        super().__init__()
        self._current_item: Optional[qw.QGraphicsItem] = None
        self.setParent(parent)

    def clear(self):
        super().clear()
        self._current_item = None

    def drawForeground(self, painter: qg.QPainter, rect: qc.QRectF) -> None:
        if self._current_item is not None:
            r = self._current_item.boundingRect()
            r = self._current_item.sceneTransform().mapRect(r)
            painter.fillRect(r, qg.QColor(0, 255, 0, 100))

    def mouseMoveEvent(self, event: qg.QMouseEvent) -> None:
        pos = self.mapToScene(event.pos())
        self._current_item = self.scene().itemAt(pos, qg.QTransform())
        self.element_selected.emit(self._current_item, pos)
        self.scene().invalidate(self.sceneRect(), qw.QGraphicsScene.ForegroundLayer)
        super().mouseMoveEvent(event)