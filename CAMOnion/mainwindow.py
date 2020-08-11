import argparse
import signal
import sys
from functools import partial
from typing import Optional
import math

from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

from CAMOnion.core.math_tools import rotate_point
from CAMOnion.ui.camo_main_window_ui import Ui_MainWindow
from CAMOnion.dialogs.origindialog import OriginDialog
from CAMOnion.widgets.positionwidget import PositionWidget
from CAMOnion.dialogs.setupdialog import SetupDialog
from CAMOnion.dialogs.featuredialog import FeatureDialog
from CAMOnion.widgets.facewidget import FaceWidget
from CAMOnion.widgets.drillwidget import DrillWidget
from CAMOnion.widgets.slotwidget import SlotWidget
from CAMOnion.core.widget_tools import get_combo_data
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
        self.new_face.triggered.connect(self.show_new_face_feature_dialog)
        self.new_drill.triggered.connect(self.show_new_drill_feature_dialog)
        self.new_slot.triggered.connect(self.show_new_slot_feature_dialog)
        self.treeView.setContextMenuPolicy(qc.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.show_r_click_tree_menu)
        self.position_widget = PositionWidget()
        self.statusbar.addWidget(self.position_widget)
        self.position_widget.change_current_origin.connect(self.change_current_origin)
        self.position_widget.change_active_setup.connect(self.change_active_setup)
        self.origin_dialog = None
        self.setup_dialog = None
        self.feature_dialog = None
        self.tree_r_click_menu = None
        self.picker_axis = None
        self.all_dxf_entities = {}
        self.selected_dxf_entities = []
        self.model_space = None
        self.right_click_point = None
        self.picked_item_vector = None
        self.scene_origin = None

        self.image = qg.QPixmap('img/splash.png')

        self.editor_setup = None
        self.editor_origin = None

        self.renderer = PyQtBackend(self.scene)
        self.doc = None
        self._render_context = None
        self._visible_layers = None
        self._current_layout = None

        self.scene_shift = (0, 0, 0)

        self.actionPost.triggered.connect(self.add_tab)

        self.hidden_dialogs = []

    def add_tab(self):
        self.feature_dialog.setHidden(not self.feature_dialog.isHidden())

    def show_r_click_tree_menu(self, point):
        self.right_click_point = point
        self.tree_r_click_menu = qw.QMenu()
        edit_tree_item_action = qw.QAction('Edit', self)
        edit_tree_item_action.triggered.connect(self.edit_tree_item)
        delete_tree_item_action = qw.QAction('Delete', self)
        delete_tree_item_action.triggered.connect(self.delete_tree_item)
        self.tree_r_click_menu.addAction(edit_tree_item_action)
        self.tree_r_click_menu.addAction(delete_tree_item_action)
        self.tree_r_click_menu.exec(self.treeView.mapToGlobal(point))
        print('rclick')

    def populate_origin_comboBox(self):
        self.position_widget.origin_combo.clear()
        for origin in self.controller.current_camo_file.origins:
            self.position_widget.origin_combo.addItem(origin.name, origin)

    def populate_active_setup_combo(self):
        self.position_widget.active_setup_combo.clear()
        for setup in self.controller.current_camo_file.setups:
            self.position_widget.active_setup_combo.addItem(setup.name, setup)

    def change_current_origin(self, origin):
        if origin:
            self.controller.current_camo_file.active_origin = origin
            self.apply_origin_to_scene()

    def change_active_setup(self, setup):
        if setup:
            self.controller.current_camo_file.active_setup = setup
            self.controller.populate_operation_list()

    def edit_tree_item(self, ):

        _, node = self.get_right_clicked_tree_item()
        if node.type == ct.OSetup:
            self.show_edit_setup_dialog(node._data[1])
        elif node.type == ct.OOrigin:
            self.show_edit_origin_dialog(node._data[1])
        print(node)

    def delete_tree_item(self):
        selected_node = self.treeView.indexAt(self.right_click_point)
        item = selected_node.internalPointer()
        print(item)
        if isinstance(item._data[1], Setup):
            self.controller.current_camo_file.setups.remove(item._data[1])
        elif isinstance(item._data[1], Origin):
            self.controller.current_camo_file.origins.remove(item._data[1])
        elif isinstance(item._data[1], PartFeature):
            self.controller.current_camo_file.features.remove(item._data[1])
        else:
            return
        self.controller.build_file_tree_model()

    def get_right_clicked_tree_item(self):
        index = self.treeView.indexAt(self.right_click_point)
        node = index.internalPointer()
        return index, node

    def show_origin_dialog(self):
        self.origin_dialog = OriginDialog()
        self.origin_dialog.find_x.clicked.connect(self.find_x)
        self.origin_dialog.find_y.clicked.connect(self.find_y)
        self.origin_dialog.buttonBox.accepted.connect(self.add_new_origin)
        self.origin_dialog.show()

    def show_edit_origin_dialog(self, origin):
        self.show_origin_dialog()
        self.editor_origin = origin
        self.origin_dialog.buttonBox.accepted.disconnect(self.add_new_origin)
        self.origin_dialog.buttonBox.accepted.connect(self.edit_origin)
        self.origin_dialog.origin_name_input.setText(origin.name)
        self.origin_dialog.origin_x.setText(str(origin.x))
        self.origin_dialog.origin_y.setText(str(origin.y))
        self.origin_dialog.angle_input.setText(str(origin.angle))
        self.origin_dialog.wfo_spinBox.setValue(origin.wfo_num)

    def add_new_origin(self):
        name, wfo, x, y, angle = self.clean_origin_values_from_dialog()
        origin = Origin(name, wfo, x, y, angle)
        self.controller.current_camo_file.origins.append(origin)
        self.controller.build_file_tree_model()
        self.populate_origin_comboBox()

    def edit_origin(self):
        name, wfo, x, y, angle = self.clean_origin_values_from_dialog()

        self.editor_origin.name = name
        self.editor_origin.x = x
        self.editor_origin.y = y
        self.editor_origin.angle = angle
        self.editor_origin.wfo_num = wfo
        self.editor_origin.angle = angle

        self.controller.build_file_tree_model()

    def clean_origin_values_from_dialog(self):
        name = self.origin_dialog.origin_name_input.text()
        x = self.origin_dialog.origin_x.text()
        y = self.origin_dialog.origin_y.text()
        angle = self.origin_dialog.angle_input.text()
        wfo = self.origin_dialog.wfo_spinBox.value()
        if x == '':
            x = 0
        if y == '':
            y = 0
        if angle == '':
            angle = 0
        return name, wfo, float(x), float(y), float(angle)

    def apply_origin_to_scene(self):
        self.reset_scene_shift()
        x = self.controller.current_camo_file.active_origin.x
        y = self.controller.current_camo_file.active_origin.y
        a = self.controller.current_camo_file.active_origin.angle
        self.scene_shift = (x, y, a)
        self.graphicsView.rotate(a)
        self.scene_origin.setX(x)
        self.scene_origin.setY(y)
        self.scene_origin.setRotation(-a)

    def reset_scene_shift(self):
        x, y, a = self.scene_shift
        self.graphicsView.rotate(360 - a)
        self.scene_origin.setX(-x)
        self.scene_origin.setY(-y)
        self.scene_origin.setRotation(a)
        self.scene_shift = (0, 0, 0)

    def show_new_setup_dialog(self):
        if len(self.controller.current_camo_file.origins) < 1:
            no_setup_message = qw.QMessageBox()
            no_setup_message.setWindowTitle('Error')
            no_setup_message.setText('Please add origin')
            no_setup_message.setIcon(no_setup_message.Critical)
            no_setup_message.exec_()
            return
        self.setup_dialog = SetupDialog(self.controller)
        self.setup_dialog.buttonBox.accepted.connect(self.add_new_setup)
        self.setup_dialog.show()

    def show_edit_setup_dialog(self, setup):
        self.setup_dialog = SetupDialog(self.controller)
        self.editor_setup = setup
        self.setup_dialog.buttonBox.accepted.connect(self.edit_setup)
        self.setup_dialog.machine_combo.setCurrentIndex(self.setup_dialog.machine_combo.findText(setup.machine.name))
        self.setup_dialog.origin_combo.setCurrentIndex(self.setup_dialog.origin_combo.findText(setup.origin.name))
        self.setup_dialog.clearance_spinbox.setValue(setup.clearance_plane)
        self.setup_dialog.setup_name_input.setText(setup.name)
        self.setup_dialog.show()

    def add_new_setup(self):
        name = self.setup_dialog.setup_name_input.text()
        machine = self.setup_dialog.machine_combo.itemData(self.setup_dialog.machine_combo.currentIndex())
        origin = self.setup_dialog.origin_combo.itemData(self.setup_dialog.origin_combo.currentIndex())
        clearance = self.setup_dialog.clearance_spinbox.value()

        setup = Setup(name, machine, origin, clearance)
        self.controller.current_camo_file.setups.append(setup)
        # self.controller.tree_model.layoutChanged.emit()
        self.controller.build_file_tree_model()

    def edit_setup(self):
        self.editor_setup.name = self.setup_dialog.setup_name_input.text()
        self.editor_setup.machine = self.setup_dialog.machine_combo.itemData(
            self.setup_dialog.machine_combo.currentIndex())
        self.editor_setup.origin = self.setup_dialog.origin_combo.itemData(
            self.setup_dialog.origin_combo.currentIndex())
        self.editor_setup.origin = self.setup_dialog.clearance_spinbox.value()
        self.controller.build_file_tree_model()

    def show_feature_dialog(self):
        if len(self.controller.current_camo_file.setups) < 1:
            no_setup_message = qw.QMessageBox()
            no_setup_message.setWindowTitle('Error')
            no_setup_message.setText('Please add setup')
            no_setup_message.setIcon(no_setup_message.Critical)
            no_setup_message.exec_()
            return
        self.feature_dialog = FeatureDialog(self.controller)

        for setup in self.controller.current_camo_file.setups:
            self.feature_dialog.setup_combo.addItem(setup.name, setup)

        self.feature_dialog.buttonBox.rejected.connect(self.feature_dialog.reject)
        self.feature_dialog.show()

    def show_face_feature_dialog(self):
        self.show_feature_dialog()
        if self.feature_dialog:
            filtered_list = [feature for feature in self.controller.feature_list.features if
                             feature.feature_type.feature_type == 'Facing']
            self.populate_filtered_base_feature_list(filtered_list)
            face_widget = FaceWidget()
            self.feature_dialog.frame_layout.addWidget(face_widget)

    def populate_filtered_base_feature_list(self, features):
        for feature in features:
            self.feature_dialog.base_feature_combo.addItem(feature.name, feature)

    def show_drill_feature_dialog(self):
        self.show_feature_dialog()
        if self.feature_dialog:
            filtered_list = [feature for feature in self.controller.feature_list.features if
                             feature.feature_type.feature_type == 'Drilling']
            self.populate_filtered_base_feature_list(filtered_list)
            self.feature_dialog.drill_widget = DrillWidget()
            self.feature_dialog.frame_layout.addWidget(self.feature_dialog.drill_widget)
            self.feature_dialog.drill_widget.select_sample_circle.clicked.connect(self.find_circle_diameter)
            self.feature_dialog.drill_widget.find_cirlces_button.clicked.connect(self.find_circles)

    def show_slot_feature_dialog(self):
        filtered_list = [feature for feature in self.controller.feature_list.features if
                         feature.feature_type.feature_type == 'Slotting']
        if len(filtered_list) < 1:
            message = qw.QMessageBox()
            message.setWindowTitle('Error')
            message.setText('Please add Slot to database Features')
            message.setIcon(message.Critical)
            message.exec_()
            return
        self.show_feature_dialog()
        if self.feature_dialog:
            self.populate_filtered_base_feature_list(filtered_list)
            self.feature_dialog.slot_widget = SlotWidget()
            self.feature_dialog.frame_layout.addWidget(self.feature_dialog.slot_widget)
            self.feature_dialog.slot_widget.add_line_button.clicked.connect(self.add_slot_line)


    def show_new_face_feature_dialog(self):
        self.show_face_feature_dialog()
        self.feature_dialog.buttonBox.accepted.connect(self.add_face_feature)

    def add_face_feature(self):
        base_feature = get_combo_data(self.feature_dialog.base_feature_combo)
        print(base_feature)
        setup = get_combo_data(self.feature_dialog.setup_combo)
        print(setup)
        feature = PartFeature(base_feature.id, setup)
        self.controller.current_camo_file.features.append(feature)
        self.controller.build_file_tree_model()

    def show_new_drill_feature_dialog(self):
        self.show_drill_feature_dialog()
        if self.feature_dialog:
            self.feature_dialog.buttonBox.accepted.connect(self.add_drill_feature)

    def show_new_slot_feature_dialog(self):
        self.show_slot_feature_dialog()
        if self.feature_dialog:
            self.feature_dialog.selected_slot_lines = []
            self.feature_dialog.buttonBox.accepted.connect(self.add_slot_feature)

    def add_slot_feature(self):
        base_feature = get_combo_data(self.feature_dialog.base_feature_combo)
        setup = get_combo_data(self.feature_dialog.setup_combo)
        geo = self.feature_dialog.selected_slot_lines
        if len(geo) > 0:
            feature = PartFeature(base_feature.id, setup, geometry=geo)
            self.controller.current_camo_file.features.append(feature)
            self.controller.build_file_tree_model()

    def add_slot_line(self):
        self.feature_dialog.hide()
        self.graphicsView.graphics_view_clicked.connect(self.dxf_entity_clicked_slot_line)

    def dxf_entity_clicked_slot_line(self, item):
        item_data = item.data(0)
        line = None
        if item_data.DXFTYPE == 'LINE':
            line = item_data
        if line:
            self.feature_dialog.selected_slot_lines.append(str(line))
            self.feature_dialog.slot_widget.line_list.addItem(str(line))
            self.feature_dialog.show()
            self.graphicsView.graphics_view_clicked.disconnect(self.dxf_entity_clicked_slot_line)

    def add_drill_feature(self):
        base_feature = get_combo_data(self.feature_dialog.base_feature_combo)
        setup = get_combo_data(self.feature_dialog.setup_combo)
        geo = self.feature_dialog.drill_widget.selected_circles
        feature = PartFeature(base_feature.id, setup, geometry=geo)
        self.controller.current_camo_file.features.append(feature)
        self.controller.build_file_tree_model()

    def find_circle_diameter(self):
        self.feature_dialog.hide()
        self.graphicsView.graphics_view_clicked.connect(self.dxf_entity_clicked_circle_diameter)

    def find_circles(self):
        diameter = self.feature_dialog.drill_widget.diameter_edit.text()
        try:

            diameter = float(diameter)
            assert diameter > 0
        except:
            message = qw.QMessageBox()
            message.setWindowTitle('Error')
            message.setText('No diameter given')
            message.setIcon(message.Critical)
            message.exec_()
            return
        circles = [entity for entity in self.controller.current_camo_file.dxf_doc.modelspace().entity_space.entities
                   if entity.DXFTYPE == 'CIRCLE']
        filtered_circles = [circle for circle in circles if math.isclose(circle.dxf.radius * 2, diameter, rel_tol=.0002)]
        self.feature_dialog.drill_widget.geometry_list.clear()
        self.feature_dialog.drill_widget.selected_circles = [str(x) for x in filtered_circles]
        for circle in filtered_circles:
            item = qw.QListWidgetItem(str(circle))
            item.circle = circle
            self.feature_dialog.drill_widget.geometry_list.addItem(item)
        self.feature_dialog.drill_widget.lcdNumber.display(len(filtered_circles))

    def dxf_entity_clicked_circle_diameter(self, item):
        item_data = item.data(0)
        diameter = None
        if item_data.DXFTYPE == 'CIRCLE':
            diameter = item_data.dxf.radius * 2
        elif item_data.DXFTYPE == 'ARC':
            diameter = item_data.dxf.radius * 2

        if diameter:
            self.feature_dialog.drill_widget.diameter_edit.setText(str(round(diameter, 4)))
            self.feature_dialog.show()
            self.graphicsView.graphics_view_clicked.disconnect(self.dxf_entity_clicked_circle_diameter)

        print(diameter)

    def find_x(self):
        self.origin_dialog.hide()
        self.picker_axis = 'x'
        self.graphicsView.graphics_view_clicked.connect(self.dxf_entity_clicked_origin)

    def find_y(self):
        self.origin_dialog.hide()
        self.picker_axis = 'y'
        self.graphicsView.graphics_view_clicked.connect(self.dxf_entity_clicked_origin)

    def fill_dxf_select_list(self, element: Optional[qw.QGraphicsItem]):
        self.selected_dxf_entities.append(element.data(0))
        print(element)

    def dxf_entity_clicked_origin(self, item):
        item_data = item.data(0)
        picked_item_vector = None
        if item_data.DXFTYPE == 'LINE':
            picked_item_vector = item_data.dxf.start
        elif item_data.DXFTYPE == 'CIRCLE':
            picked_item_vector = item_data.dxf.center
        elif item_data.DXFTYPE == 'ARC':
            picked_item_vector = item_data.dxf.center

        if picked_item_vector:
            if self.picker_axis == 'x':
                self.origin_dialog.origin_x.setText(str(round(picked_item_vector.x, 4)))
            elif self.picker_axis == 'y':
                self.origin_dialog.origin_y.setText(str(round(picked_item_vector.y, 4)))
        self.origin_dialog.showNormal()
        self.graphicsView.graphics_view_clicked.disconnect(self.dxf_entity_clicked_origin)

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


    def draw_origin(self):
        pen = qg.QPen(qg.QColor('#e533e5'), 2)
        pen.setCosmetic(True)  # changes width depending on zoom
        pen.setJoinStyle(qc.Qt.RoundJoin)

        length = self.scene.itemsBoundingRect().width() / 16
        diameter = length / 10

        origin_item = qw.QGraphicsItemGroup()

        circle = qw.QGraphicsEllipseItem(qc.QRectF(-diameter / 2, -diameter / 2, diameter, diameter))
        circle.setPen(pen)
        circle.setEnabled(False)
        origin_item.addToGroup(circle)

        x_line = qw.QGraphicsLineItem(0, 0, length, 0, )
        x_line.setPen(pen)
        origin_item.addToGroup(x_line)

        y_line = qw.QGraphicsLineItem(0, 0, 0, length)
        y_line.setPen(pen)
        origin_item.addToGroup(y_line)

        origin_item.setEnabled(False)
        origin_item.setZValue(-1)
        self.scene_origin = origin_item
        self.scene.addItem(self.scene_origin)

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
        self.draw_origin()
        self.apply_origin_to_scene()

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
        shifted_position = (mouse_pos.x()-self.scene_shift[0], mouse_pos.y()-self.scene_shift[1])
        x, y = shifted_position
        x, y = rotate_point((x, y), -self.scene_shift[2])

        # rotate also here
        text = f'mouse position: {shifted_position[0]:.4f}, {shifted_position[1]:.4f}\n'
        self.position_widget.xlabel.setText(f'X: {x:.4f}')
        self.position_widget.ylabel.setText(f'Y: {y:.4f}')
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



