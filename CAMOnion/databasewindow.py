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
        self.dialog = None
        self.operation_window = None
        self.add_tool_button.clicked.connect(self.test)
        self.tool_list_widget.doubleClicked.connect(self.tool_selected)

    def tool_selected(self):
        all_types = [self.tool_type_combo.itemText(i) for i in range(self.tool_type_combo.count())]
        tool = self.tool_list_widget.selectedItems()[0].tool
        print(tool)
        self.diameter_input.setText(str(tool.diameter))
        for i, _type in enumerate(all_types):
            if _type == tool._type.tool_type:
                self.tool_type_combo.setCurrentIndex(i)
        print(self.tool_type_combo.currentText())

    def show_operation_window(self):
        self.operation_window = OperationWindow()
        self.operation_window.show()

    def populate_tool_list_widget(self):
        if self.controller.tool_list:
            tools = self.controller.tool_list.tools
            for i, tool in enumerate(tools):
                self.tool_list_widget.addItem(ToolTableWidgetItem(tool))
        self.tool_list_widget.repaint()

    def populate_tool_types(self):
        if not self.controller.tool_list:
            self.controller.test_db()
        for tool_type in self.controller.tool_list.types:
            self.tool_type_combo.addItem(tool_type.tool_type, tool_type)



    def test(self):
        index = self.op_type_combo.currentIndex()
        print(self.op_type_combo.itemData(index).id)


class ToolTableWidgetItem(qw.QListWidgetItem):
    def __init__(self, tool):
        self.tool = tool
        self.string = f'{self.tool.name} - {self.tool.diameter}'
        super().__init__(self.string)


