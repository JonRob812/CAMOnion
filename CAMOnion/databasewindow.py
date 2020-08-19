from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui

from CAMOnion.ui.camo_database_window_ui import Ui_databaseWindow
from CAMOnion.operationwindow import OperationWindow
from CAMOnion.utils import CNCCalc
from CAMOnion.database.tables import CamoOp


class databaseWindow(qw.QMainWindow, Ui_databaseWindow):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
        self.add_op_button.clicked.connect(self.new_op)
        self.delete_op_button.clicked.connect(self.delete_op)
        self.populate_tool_list_widget(self.tool_list_widget)
        self.populate_tool_types()
        self.populate_feature_types()
        self.populate_feature_list_widget()
        self.populate_machine_list_widget()
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
        self.feature_op_list.doubleClicked.connect(self.selected_feature_op)
        self.tool_list_widget.doubleClicked.connect(self.tool_selected)
        self.machine_list.doubleClicked.connect(self.machine_selected)
        self.add_machine_button.clicked.connect(self.add_machine)
        self.remove_machine_button.clicked.connect(self.delete_machine)
        self.edit_machine_button.clicked.connect(self.edit_machine)

        self.editor_tool = None
        self.editor_feature = None
        self.editor_op = None
        self.editor_machine = None

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
        for i, _type in enumerate(
                [self.feature_type_combo.itemText(i) for i in range(self.feature_type_combo.count())]):
            if _type == feature.feature_type.feature_type:
                self.feature_type_combo.setCurrentIndex(i)
        self.feature_desc_input.setText(feature.description)
        self.populate_feature_op_list()

    def machine_selected(self):
        machine = self.machine_list.selectedItems()[0].machine
        self.editor_machine = machine
        self.mach_name.setText(machine.name)
        self.mach_rpm.setText(str(machine.max_rpm))
        self.mach_spot.setText(str(machine.spot))
        self.mach_drill.setText(str(machine.drill))
        self.mach_tap.setText(str(machine.tap))
        self.mach_peck.setText(str(machine.peck))
        self.mach_ream.setText(str(machine.ream))
        self.mach_countersink.setText(str(machine.countersink))
        self.mach_drill_format.setText(machine.drill_format)
        self.mach_tap_format.setText(machine.tap_format)
        self.mach_program_start.setText(machine.program_start)
        self.mach_program_end.setText(machine.program_end)
        self.mach_op_start.setText(machine.op_start)
        self.mach_tool_start.setText(machine.tool_start)
        self.mach_tool_end.setText(machine.tool_end)

    def add_machine(self):
        if self.mach_name.text() not in [machine.name for machine in self.controller.machine_list.machines]:
            machine = self.controller.machine_list.safe_add(
                self.mach_name.text(),
                self.mach_rpm.text(),
                self.mach_spot.text(),
                self.mach_drill.text(),
                self.mach_tap.text(),
                self.mach_peck.text(),
                self.mach_ream.text(),
                self.mach_countersink.text(),
                self.mach_drill_format.toPlainText(),
                self.mach_tap_format.toPlainText(),
                self.mach_program_start.toPlainText(),
                self.mach_program_end.toPlainText(),
                self.mach_tool_start.toPlainText(),
                self.mach_tool_end.toPlainText(),
                self.mach_op_start.toPlainText(),
            )
            if machine:
                self.editor_machine = machine
                self.populate_machine_list_widget()

    def delete_machine(self):
        if self.editor_machine:
            self.controller.machine_list.delete(self.editor_machine.id)
            self.editor_machine = None
            self.populate_machine_list_widget()

    def edit_machine(self):
        if self.editor_machine:
            machine = self.editor_machine
            self.controller.machine_list.safe_edit(machine,
                                                   self.mach_name.text(),
                                                   self.mach_rpm.text(),
                                                   self.mach_spot.text(),
                                                   self.mach_drill.text(),
                                                   self.mach_tap.text(),
                                                   self.mach_peck.text(),
                                                   self.mach_ream.text(),
                                                   self.mach_countersink.text(),
                                                   self.mach_drill_format.toPlainText(),
                                                   self.mach_tap_format.toPlainText(),
                                                   self.mach_program_start.toPlainText(),
                                                   self.mach_program_end.toPlainText(),
                                                   self.mach_tool_start.toPlainText(),
                                                   self.mach_tool_end.toPlainText(),
                                                   self.mach_op_start.toPlainText(),
                                                   )
            self.populate_machine_list_widget()

    def delete_feature(self):
        if self.editor_feature:
            self.controller.feature_list.delete(self.editor_feature.id)
            self.populate_feature_list_widget()
            self.clear_feature_inputs()

    def tool_input_values(self):
        return self.diameter_input.text(), self.tool_number_input.text(), self.tool_type_combo.itemData(
            self.tool_type_combo.currentIndex()).id, self.tool_name_input.text(), self.qb_id_input.text(), self.num_flutes_input.text(), self.tap_pitch_input.text()

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
                self.populate_tool_list_widget(self.tool_list_widget)

    def feature_input_values(self):
        return self.feature_name_input.text(), self.feature_desc_input.text(), self.feature_type_combo.itemData(
            self.feature_type_combo.currentIndex()).id

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
        tool_dict = self.controller.tool_list.get_valid_tool_dict(*self.tool_input_values())
        if tool_dict:
            tool = self.controller.tool_list.add_from_dict(tool_dict)
            self.editor_tool = tool
            self.populate_tool_list_widget(self.tool_list_widget)
            self.clear_tool_inputs()

    def delete_tool(self):
        if self.editor_tool:
            self.controller.tool_list.delete(self.editor_tool.id)
            self.populate_tool_list_widget(self.tool_list_widget)
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
        self.populate_tool_list_widget(self.operation_window.op_tool_list)
        self.operation_window.set_rpm_button.clicked.connect(self.set_rpm)
        self.operation_window.set_feedrate_buuton.clicked.connect(self.set_feedrate)
        self.operation_window.buttonBox.accepted.connect(self.confirm_op)
        self.populate_op_types()
        self.operation_window.buttonBox.rejected.connect(self.operation_window.close)
        self.operation_window.show()

    def populate_tool_list_widget(self, widget):
        widget.clear()
        if self.controller.tool_list:
            tools = self.controller.tool_list.tools
            sorted_tools = sorted(sorted(tools, key=lambda t: t.diameter), key=lambda t: t.tool_type.tool_type)
            for i, tool in enumerate(sorted_tools):
                item = ToolListWidgetItem(tool)
                if tool.tool_type.tool_type == 'Drill':
                    item.setIcon(QtGui.QIcon(':img/drill.png'))
                widget.addItem(item)
        widget.repaint()

    def populate_machine_list_widget(self):
        self.machine_list.clear()
        for machine in self.controller.machine_list.machines:
            self.machine_list.addItem(MachineListWidgetItem(machine))
        self.machine_list.repaint()

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

    def populate_op_types(self):
        if not self.controller.feature_list:
            self.controller.test_db()
        if self.editor_feature:

            selected_feature_type = self.editor_feature.feature_type
            camo_ops = self.controller.session.query(CamoOp).filter(CamoOp.feature_type == selected_feature_type)
            for _type in camo_ops:
                self.operation_window.op_type_combo.addItem(_type.op_type, _type)

    def add_feature(self):
        name = self.feature_name_input.text()
        desc = self.feature_desc_input.text()
        type_id = self.feature_type_combo.itemData(self.feature_type_combo.currentIndex()).id
        feature_dict = self.controller.feature_list.get_valid_feature_dict(name, desc, type_id)
        if feature_dict:
            if feature_dict['name'] not in [feature.name for feature in self.controller.feature_list.features]:
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

    def new_op(self):
        self.editor_op = None
        self.show_operation_window()

    def delete_op(self):
        if self.feature_op_list.selectedItems():
            op_id = self.feature_op_list.selectedItems()[0].op.id
            self.controller.operation_list.delete(op_id)
            self.populate_feature_op_list()

    def confirm_op(self):

        feature = self.editor_feature
        if self.operation_window.op_tool_list.selectedItems():
            tool = self.operation_window.op_tool_list.selectedItems()[0].tool
        else:
            return

        camo_op = self.operation_window.op_type_combo.itemData(self.operation_window.op_type_combo.currentIndex())
        rpm = self.operation_window.rpm_input.text()
        feedrate = self.operation_window.feed_rate_input.text()
        peck = self.operation_window.peck_input.text()

        if self.editor_op:
            self.controller.operation_list.safe_edit(self.editor_op, feature, tool, camo_op, feedrate, rpm, peck)
        else:
            self.editor_op = self.controller.operation_list.safe_add(feature, tool, camo_op, feedrate, rpm, peck)
        self.populate_feature_op_list()
        self.operation_window.close()

    def apply_op_changes(self):
        pass

    def populate_feature_op_list(self):
        self.feature_op_list.clear()
        if self.editor_feature:
            for op in self.editor_feature.operations:
                self.feature_op_list.addItem(FeatureOpListWidgetItem(op))
            self.feature_op_list.repaint()

    def set_rpm(self):
        tool = self.operation_window.op_tool_list.selectedItems()[0].tool
        sfpm = self.operation_window.sfpm_input.text()
        if sfpm == '':
            return
        if tool:
            dia = float(tool.diameter)
            self.operation_window.rpm_input.setText(str(CNCCalc.rpm(dia, sfpm)))

    def set_feedrate(self):
        tool = self.operation_window.op_tool_list.selectedItems()[0].tool
        rpm = self.operation_window.rpm_input.text()
        ipr_ipf = self.operation_window.feed_input.text()
        if rpm == '' or ipr_ipf == '':
            return
        if tool:
            if tool.tool_type.tool_type == 'Drill' or tool.tool_type.tool_type == 'Spot':
                flutes = 1
            else:
                flutes = tool.number_of_flutes
            if tool.tool_type.tool_type == 'Tap':
                self.operation_window.feed_rate_input.setText(str(tool.pitch))
                return
            self.operation_window.feed_rate_input.setText(
                str(CNCCalc.feedrate(rpm, ipr_ipf, flutes)))

    def selected_feature_op(self):
        print('me')
        self.editor_op = self.feature_op_list.selectedItems()[0].op
        self.show_operation_window()
        self.load_op_into_window()

    def load_op_into_window(self):
        operation = self.editor_op
        for i, op in enumerate([self.operation_window.op_type_combo.itemText(i) for i in
                                range(self.operation_window.op_type_combo.count())]):
            if op == operation.camo_op.op_type:
                self.operation_window.op_type_combo.setCurrentIndex(i)
        self.operation_window.rpm_input.setText(str(round(operation.speed)))
        self.operation_window.feed_rate_input.setText(str(round(operation.feed, 2)))
        self.operation_window.peck_input.setText(str(round(operation.peck, 4)))
        item_list = [self.operation_window.op_tool_list.item(i) for i in
                     range(self.operation_window.op_tool_list.count())]
        if self.editor_op.tool:
            for i, item in enumerate(item_list):
                if item.tool.id == self.editor_op.tool.id:
                    self.operation_window.op_tool_list.setCurrentRow(self.operation_window.op_tool_list.row(item))

    def delete_feature_op(self):
        if self.feature_op_list.selectedItems():
            selected_op = self.feature_op_list.selectedItems()[0].op
            self.controller.operation_list.delete(selected_op.id)
            self.populate_feature_op_list()


class ToolListWidgetItem(qw.QListWidgetItem):
    def __init__(self, tool):
        self.tool = tool
        self.string = f'{self.tool.diameter:^12} - {self.tool.tool_type.tool_type:<18} - {self.tool.name:<25} - T{self.tool.tool_number:<3} '
        super().__init__(self.string)


class FeatureListWidgetItem(qw.QListWidgetItem):
    def __init__(self, feature):
        self.feature = feature
        self.string = f'{self.feature.feature_type.feature_type:<15} - {self.feature.name:>15}'
        super().__init__(self.string)


class FeatureOpListWidgetItem(qw.QListWidgetItem):
    def __init__(self, op):
        self.op = op
        if op.tool:
            tool_name = op.tool.name
        else:
            tool_name = 'No Tool'
        self.string = f'{self.op.camo_op.op_type} - {tool_name} - RPM: {round(self.op.speed)} Feed: {round(self.op.feed, 1)} Peck: {self.op.peck}'
        super().__init__(self.string)


class MachineListWidgetItem(qw.QListWidgetItem):
    def __init__(self, machine):
        self.machine = machine
        self.string = f'{machine.name}'
        super().__init__(self.string)

