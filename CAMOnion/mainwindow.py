import argparse
import signal
import sys
from functools import partial
from typing import Optional

from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

from CAMOnion.ui.camo_main_window_ui import Ui_MainWindow
from CAMOnion.dialogs.origindialog import OriginDialog
from CAMOnion.widgets.positionwidget import PositionWidget
from CAMOnion.dialogs.setupdialog import SetupDialog
from CAMOnion.dialogs.featuredialog import FeatureDialog

from CAMOnion.core import Setup, Origin, PartFeature, PartOperation, CamoOp, CamoItemTypes as ct

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import PyQtBackend, CorrespondingDXFEntity, \
    CorrespondingDXFEntityStack
from ezdxf.drawing import Drawing
from ezdxf.addons import Importer

from copy import copy


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
        self.actionImport_DXF.triggered.connect(self.import_dxf)
        self.actionNew_Origin.triggered.connect(self.show_origin_dialog)
        self.actionNew_Setup.triggered.connect(self.show_new_setup_dialog)
        self.actionNew_Feature.triggered.connect(self.show_new_feature_dialog)
        self.treeView.setContextMenuPolicy(qc.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.show_r_click_tree_menu)
        self.position_widget = PositionWidget()
        self.statusbar.addWidget(self.position_widget)
        self.origin_dialog = None
        self.setup_dialog = None
        self.feature_dialog = None
        self.tree_r_click_menu = None
        self.picker_axis = None
        self.all_dxf_entities = {}
        self.selected_dxf_entities = []
        self.model_space = None
        self.right_click_point = None

        self.editor_setup = None

        self.renderer = PyQtBackend(self.scene)
        self.doc = None
        self._render_context = None
        self._visible_layers = None
        self._current_layout = None

    def show_r_click_tree_menu(self, point):
        self.right_click_point = point
        self.tree_r_click_menu = qw.QMenu()
        edit_tree_item_action = qw.QAction('Edit', self)
        edit_tree_item_action.triggered.connect(self.edit_tree_item)
        delete_tree_item_action = qw.QAction('Delete', self)
        self.tree_r_click_menu.addAction(edit_tree_item_action)
        self.tree_r_click_menu.addAction(delete_tree_item_action)
        self.tree_r_click_menu.exec(self.treeView.mapToGlobal(point))
        print('rclick')

    def edit_tree_item(self,):
        index = self.treeView.indexAt(self.right_click_point)
        node = index.internalPointer()
        if node.type == ct.OSetup:
            self.show_edit_setup_dialog(node._data[1])
        print(node)

    def show_origin_dialog(self):
        self.origin_dialog = OriginDialog()
        self.origin_dialog.find_x.clicked.connect(self.find_x)
        self.origin_dialog.find_y.clicked.connect(self.find_y)
        self.origin_dialog.buttonBox.accepted.connect(self.add_new_origin)
        self.origin_dialog.show()

    def add_new_origin(self):
        name = self.origin_dialog.origin_name_input.text()
        x = str(self.origin_dialog.x_entity)
        y = str(self.origin_dialog.y_entity)
        origin = Origin(name, x, y)
        self.controller.current_camo_file.origins.append(origin)
        self.controller.build_file_tree_model()

    def show_new_setup_dialog(self):
        self.setup_dialog = SetupDialog(self.controller)
        self.setup_dialog.buttonBox.accepted.connect(self.add_new_setup)
        self.setup_dialog.show()

    def show_edit_setup_dialog(self, setup):
        self.setup_dialog = SetupDialog(self.controller)
        self.editor_setup = setup
        self.setup_dialog.buttonBox.accepted.connect(self.edit_setup)
        self.setup_dialog.machine_combo.setCurrentIndex(self.setup_dialog.machine_combo.findText(setup.machine.name))
        self.setup_dialog.origin_combo.setCurrentIndex(self.setup_dialog.origin_combo.findText(setup.origin.name))
        self.setup_dialog.setup_name_input.setText(setup.name)
        self.setup_dialog.show()

    def add_new_setup(self):
        name = self.setup_dialog.setup_name_input.text()
        machine = self.setup_dialog.machine_combo.itemData(self.setup_dialog.machine_combo.currentIndex())
        origin = self.setup_dialog.origin_combo.itemData(self.setup_dialog.origin_combo.currentIndex())

        setup = Setup(name, machine, origin)
        self.controller.current_camo_file.setups.append(setup)
        # self.controller.tree_model.layoutChanged.emit()
        self.controller.build_file_tree_model()

    def edit_setup(self):
        self.editor_setup.name = self.setup_dialog.setup_name_input.text()
        self.editor_setup.machine = self.setup_dialog.machine_combo.itemData(self.setup_dialog.machine_combo.currentIndex())
        self.editor_setup.origin = self.setup_dialog.origin_combo.itemData(self.setup_dialog.origin_combo.currentIndex())
        self.controller.build_file_tree_model()

    def add_feature(self):
        pass

    def edit_feature(self):
        pass

    def delete_tree_item(self):
        pass

    def show_new_feature_dialog(self):
        self.feature_dialog = FeatureDialog(self.controller)
        self.feature_dialog.show()

    def find_x(self):
        self.origin_dialog.hide()
        self.picker_axis = 'x'
        self.graphicsView.graphics_view_clicked.connect(self.window_clicked)

    def find_y(self):
        self.origin_dialog.hide()
        self.picker_axis = 'y'
        self.graphicsView.graphics_view_clicked.connect(self.window_clicked)

    def window_clicked(self, item):
        if self.picker_axis == 'x':
            self.origin_dialog.origin_x.setText(str(item.data(0)))
            self.origin_dialog.x_entity = item.data(0)
        elif self.picker_axis == 'y':
            self.origin_dialog.origin_y.setText(str(item.data(0)))
            self.origin_dialog.y_entity = item.data(0)
        self.origin_dialog.showNormal()
        self.graphicsView.graphics_view_clicked.disconnect(self.window_clicked)

    def import_dxf(self):
        path, _ = qw.QFileDialog.getOpenFileName(self, caption='Select CAD Document', filter='DXF Documents (*.dxf)')
        if path:
            incoming_dxf = ezdxf.readfile(path)
            importer = Importer(incoming_dxf, self.controller.current_camo_file.dxf_doc)
            # import all entities from source modelspace into modelspace of the target drawing
            importer.import_modelspace()
            importer.finalize()
            self.set_document(self.controller.current_camo_file.dxf_doc)
            self.controller.build_file_tree_model()

    def set_document(self, document: Drawing):
        self.doc = document
        self._render_context = RenderContext(document)
        self._visible_layers = None
        self._current_layout = None
        # self._populate_layouts()
        self._populate_layer_list()
        self.draw_layout('Model')
        self.model_space = self.doc.modelspace()
        self.all_dxf_entities = {}
        for entity in self.model_space.entity_space:
            self.all_dxf_entities[str(entity)] = entity

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

    # def _populate_layouts(self):
    #     self.select_layout_menu.clear()
    #     for layout_name in self.doc.layout_names_in_taborder():
    #         action = qw.QAction(layout_name, self)
    #         action.triggered.connect(partial(self.draw_layout, layout_name))
    #         self.select_layout_menu.addAction(action)

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
                attribs = dxf_entity.dxf.all_existing_dxf_attribs()
                for key, value in attribs.items():
                    text += f'- {key}: {value}\n'
                if 'start' in attribs:
                    self.position_widget.xlabel.setText('X:' + str(round(attribs['start'][0], 4)))
                    self.position_widget.ylabel.setText('Y:' + str(round(attribs['start'][1], 4)))
                elif 'center' in attribs:
                    self.position_widget.xlabel.setText('X:' + str(round(attribs['center'][0], 4)))
                    self.position_widget.ylabel.setText('Y:' + str(round(attribs['center'][1], 4)))

                dxf_entity_stack = element.data(CorrespondingDXFEntityStack)

                # model = self.controller.main_window.treeView.model()
                # view = self.treeView
                # if model and model.indexes:     this doe the tree select based on hover
                #     view.setCurrentIndex(model.indexes[str(dxf_entity)])

                if dxf_entity_stack:
                    text += '\nParents:\n'
                    for entity in reversed(dxf_entity_stack):
                        text += f'- {entity}\n'

        self.info.setPlainText(text)

    @qc.pyqtSlot(object, qc.QPointF)
    def fill_dxf_select_list(self, element: Optional[qw.QGraphicsItem], mouse_pos: qc.QPointF):
        self.selected_dxf_entities.append(element.data(0))





