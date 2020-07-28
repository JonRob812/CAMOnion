import argparse
import signal
import sys
from functools import partial
from typing import Optional

from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg
from CAMOnion.ui.camo_main_window_ui import Ui_MainWindow

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import _get_x_scale, PyQtBackend, CorrespondingDXFEntity, \
    CorrespondingDXFEntityStack
from ezdxf.drawing import Drawing


class MainWindow(qw.QMainWindow, Ui_MainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
        self.scene = qw.QGraphicsScene()
        self.view = self.graphicsView
        self.view.setScene(self.scene)
        self.view.scale(1, -1)  # so that +y is up
        self.view.element_selected.connect(self._on_element_selected)
        self.actionImport_DXF.triggered.connect(self._select_doc)

        self.renderer = PyQtBackend(self.scene)
        self.doc = None
        self._render_context = None
        self._visible_layers = None
        self._current_layout = None

    def draw_circle(self):
        pass

    def _select_doc(self):
        path, _ = qw.QFileDialog.getOpenFileName(self, caption='Select CAD Document', filter='DXF Documents (*.dxf)')
        if path:
            self.set_document(ezdxf.readfile(path, legacy_mode=True))

    def set_document(self, document: Drawing):
        self.doc = document
        self._render_context = RenderContext(document)
        self._visible_layers = None
        self._current_layout = None
        self._populate_layouts()
        self._populate_layer_list()
        self.draw_layout('Model')
        print('noth')

    def _populate_layer_list(self):
        self.layers.blockSignals(True)
        self.layers.clear()
        for layer in self._render_context.layers.values():
            name = layer.layer
            item = qw.QListWidgetItem(name)
            item.setCheckState(qc.Qt.Checked)
            item.setBackground(qg.QColor(layer.color))
            self.layers.addItem(item)
        self.layers.blockSignals(False)

    def _populate_layouts(self):
        self.select_layout_menu.clear()
        for layout_name in self.doc.layout_names_in_taborder():
            action = qw.QAction(layout_name, self)
            action.triggered.connect(partial(self.draw_layout, layout_name))
            self.select_layout_menu.addAction(action)

    def draw_layout(self, layout_name: str):
        print(f'drawing {layout_name}')
        self._current_layout = layout_name
        self.renderer.clear()
        self.view.clear()
        layout = self.doc.layout(layout_name)
        self._update_render_context(layout)
        Frontend(self._render_context, self.renderer).draw_layout(layout)
        self.view.fit_to_scene()

    def _update_render_context(self, layout):
        assert self._render_context
        self._render_context.set_current_layout(layout)
        # Direct modification of RenderContext.layers would be more flexible, but would also expose the internals.
        if self._visible_layers is not None:
            self._render_context.set_layers_state(self._visible_layers, state=True)

    def resizeEvent(self, event: qg.QResizeEvent) -> None:
        self.view.fit_to_scene()

    @qc.pyqtSlot(qw.QListWidgetItem)
    def _layers_updated(self, _item: qw.QListWidgetItem):
        self._visible_layers = set()
        for i in range(self.layers.count()):
            layer = self.layers.item(i)
            if layer.checkState() == qc.Qt.Checked:
                self._visible_layers.add(layer.text())
        self.draw_layout(self._current_layout)

    @qc.pyqtSlot()
    def _toggle_sidebar(self):
        self.sidebar.setHidden(not self.sidebar.isHidden())

    @qc.pyqtSlot()
    def _toggle_join_polylines(self):
        self.renderer.draw_individual_polyline_elements = not self.renderer.draw_individual_polyline_elements
        self.draw_layout(self._current_layout)

    @qc.pyqtSlot(object, qc.QPointF)
    def _on_element_selected(self, element: Optional[qw.QGraphicsItem], mouse_pos: qc.QPointF):
        text = f'mouse position: {mouse_pos.x():.4f}, {mouse_pos.y():.4f}\n'
        if element is None:
            text += 'No element selected'
        else:
            dxf_entity = element.data(CorrespondingDXFEntity)
            if dxf_entity is None:
                text += 'No data'
            else:
                text += f'Current Entity: {dxf_entity}\nLayer: {dxf_entity.dxf.layer}\n\nDXF Attributes:\n'
                for key, value in dxf_entity.dxf.all_existing_dxf_attribs().items():
                    text += f'- {key}: {value}\n'

                dxf_entity_stack = element.data(CorrespondingDXFEntityStack)
                if dxf_entity_stack:
                    text += '\nParents:\n'
                    for entity in reversed(dxf_entity_stack):
                        text += f'- {entity}\n'

        self.info.setPlainText(text)
        self.statusbar.showMessage(text)

