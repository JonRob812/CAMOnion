from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui

from CAMOnion.ui.camo_database_window_ui import Ui_databaseWindow
from CAMOnion.operationwindow import OperationWindow
from CAMOnion.data_models.tool_list import ToolList
from CAMOnion.database.db_utils import get_session


class databaseWindow(qw.QMainWindow, Ui_databaseWindow):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
        self.add_op_button.clicked.connect(self.show_operation_window)
        self.populate_tool_list_widget()
        self.populate_tool_types()
        self.populate_feature_types()
        self.populate_feature_list_widget()
        self.dialog = None
        self.operation_window = None
        self.tool_list_widget.doubleClicked.connect(self.tool_selected)
        self.feature_list.doubleClicked.connect(self.feature_selected)
        self.apply_changes_tool_button.clicked.connect(self.apply_changes_tool)
        self.apply_feature_changes_button.clicked.connect(self.apply_changes_feature)
        self.add_tool_button.clicked.connect(self.add_tool)
        self.delete_tool_button.clicked.connect(self.delete_tool)
        self.tool_type_combo.currentIndexChanged.connect(self.tool_type_combo_changed_event)
        self.add_feature_button.clicked.connect(self.add_feature)
        self.delete_feature_button.clicked.connect(self.delete_feature)

        self.editor_tool = None
        self.editor_feature = None

    def tool_selected(self):
        tool = self.tool_list_widget.selectedItems()[0].tool
        self.editor_tool = tool
        print(tool)
        self.diameter_input.setText(str(tool.diameter))
        all_types = [self.tool_type_combo.itemText(i) for i in range(self.tool_type_combo.count())]
        for i, _type in enumerate(all_types):
            if _type == tool.tool_type.tool_type:
                self.tool_type_combo.setCurrentIndex(i)
        self.tool_number_input.setText(str(self.editor_tool.tool_number))
        self.qb_id_input.setText(str(self.editor_tool.qb_id))
        self.tool_name_input.setText(self.editor_tool.name)
        self.num_flutes_input.setText(str(self.editor_tool.number_of_flutes))
        self.tap_pitch_input.setText(str(self.editor_tool.pitch))
        print(self.tool_type_combo.currentText())

    def feature_selected(self):
        feature = self.feature_list.selectedItems()[0].feature
        self.editor_feature = feature
        self.feature_name_input.setText(feature.name)
        for i, _type in enumerate([self.feature_type_combo.itemText(i) for i in range(self.feature_type_combo.count())]):
            if _type == feature.feature_type.feature_type:
                self.feature_type_combo.setCurrentIndex(i)
        self.feature_desc_input.setText(feature.description)

    def delete_feature(self):
        if self.editor_feature:
            self.controller.feature_list.delete(self.editor_feature.id)
            self.populate_feature_list_widget()
            self.clear_feature_inputs()

    def tool_input_values(self):
        return self.diameter_input.text(), self.tool_number_input.text(), self.tool_type_combo.itemData(self.tool_type_combo.currentIndex()).id, self.tool_name_input.text(), self.qb_id_input.text(), self.num_flutes_input.text(), self.tap_pitch_input.text()

    def apply_changes_tool(self):
        if self.editor_tool:
            tool_dict = self.controller.tool_list.get_valid_tool_dict(*self.tool_input_values())
            if tool_dict:
                self.editor_tool.diameter = tool_dict['diameter']
                self.editor_tool.tool_number = tool_dict['tool_number']
                self.editor_tool.tool_type_id = tool_dict['tool_type_id']
                self.editor_tool.name = tool_dict['name']
                self.editor_tool.qb_id = tool_dict['qb_id']
                self.editor_tool.number_of_flutes = tool_dict['num_flutes']
                self.editor_tool.pitch = tool_dict['pitch']
                self.controller.session.commit()
                self.controller.tool_list.refresh()
                self.populate_tool_list_widget()

    def feature_input_values(self):
        return self.feature_name_input.text(), self.feature_desc_input.text(), self.feature_type_combo.itemData(self.feature_type_combo.currentIndex()).id

    def apply_changes_feature(self):
        if self.editor_feature:
            feature_dict = self.controller.feature_list.get_valid_feature_dict(*self.feature_input_values())
            if feature_dict:
                self.editor_feature.name = feature_dict['name']
                self.editor_feature.description = feature_dict['desc']
                self.editor_feature.type_id = feature_dict['type_id']
                self.controller.session.commit()
                self.controller.feature_list.refresh()
                self.populate_feature_list_widget()

    def add_tool(self):
        tool_dict = self.controller.tool_list.get_valid_tool_dict(self.tool_input_values())
        if tool_dict:
            tool = self.controller.tool_list.add_from_dict(tool_dict)
            self.editor_tool = tool
            self.populate_tool_list_widget()
            self.clear_tool_inputs()

    def delete_tool(self):
        if self.editor_tool:
            self.controller.tool_list.delete(self.editor_tool.id)
            self.populate_tool_list_widget()
            self.clear_tool_inputs()

    def clear_tool_inputs(self):
        self.editor_tool = None
        self.diameter_input.clear()
        self.tool_type_combo.repaint()
        self.tool_number_input.clear()
        self.qb_id_input.clear()
        self.tool_name_input.clear()
        self.num_flutes_input.clear()
        self.tap_pitch_input.clear()

    def clear_feature_inputs(self):
        self.feature_name_input.clear()
        self.feature_type_combo.repaint()
        self.feature_desc_input.clear()


    def tool_type_combo_changed_event(self):
        if self.tool_type_combo.currentText() == 'Tap':
            self.tap_pitch_input.setDisabled(False)
        else:
            self.tap_pitch_input.setDisabled(True)

    def show_operation_window(self):
        self.operation_window = OperationWindow()
        self.operation_window.show()

    def populate_tool_list_widget(self):
        self.tool_list_widget.clear()
        if self.controller.tool_list:
            tools = self.controller.tool_list.tools
            sorted_tools = sorted(sorted(tools, key=lambda t: t.diameter), key=lambda t: t.tool_type.tool_type)
            for i, tool in enumerate(sorted_tools):
                self.tool_list_widget.addItem(ToolListWidgetItem(tool))
        self.tool_list_widget.repaint()

    def populate_tool_types(self):
        if not self.controller.tool_list:
            self.controller.test_db()
        for tool_type in self.controller.tool_list.types:
            self.tool_type_combo.addItem(tool_type.tool_type, tool_type)
        self.tool_type_combo_changed_event()

    def populate_feature_types(self):
        if not self.controller.feature_list:
            self.controller.test_db()
        for feature_type in self.controller.feature_list.types:
            self.feature_type_combo.addItem(feature_type.feature_type, feature_type)

    def add_feature(self):
        name = self.feature_name_input.text()
        desc = self.feature_desc_input.text()
        type_id = self.feature_type_combo.itemData(self.feature_type_combo.currentIndex()).id
        feature_dict = self.controller.feature_list.get_valid_feature_dict(name, desc, type_id)
        if feature_dict:
            feature = self.controller.feature_list.add_from_dict(feature_dict)
            self.editor_feature = feature
            self.populate_feature_list_widget()

    def populate_feature_list_widget(self):
        self.feature_list.clear()
        if self.controller.feature_list:
            features = self.controller.feature_list.features
            for i, feature in enumerate(features):
                self.feature_list.addItem(FeatureListWidgetItem(feature))
            self.feature_list.repaint()


class ToolListWidgetItem(qw.QListWidgetItem):
    def __init__(self, tool):
        self.tool = tool
        self.string = f'T{self.tool.tool_number} - {self.tool.name} - {self.tool.diameter} - {self.tool.tool_type.tool_type}'
        super().__init__(self.string)


class FeatureListWidgetItem(qw.QListWidgetItem):
    def __init__(self, feature):
        self.feature = feature
        self.string = f'{self.feature.feature_type.feature_type} - {self.feature.name}'
        super().__init__(self.string)
