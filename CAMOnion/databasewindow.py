from PyQt5 import QtWidgets as qw

from CAMOnion.ui.camo_database_window_ui import Ui_databaseWindow
from CAMOnion.connectwindow import ConnectWindow
from CAMOnion.operationwindow import OperationWindow
from CAMOnion.data_models.tool_list import ToolListModel
from CAMOnion.database.db_utils import get_session


class databaseWindow(qw.QMainWindow, Ui_databaseWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
        self.actionConnect.triggered.connect(self.show_connect_dialog)
        self.add_op_button.clicked.connect(self.show_operation_window)
        self.dialog = None
        self.operation_window = None
        if not self.controller.session:
            self.controller.setup_sql()
        self.tableView.setModel(ToolListModel(self.controller.session))

    def show_connect_dialog(self):
        self.dialog = ConnectWindow(self.controller)
        self.dialog.show()

    def show_operation_window(self):
        self.operation_window = OperationWindow()
        self.operation_window.show()

    def populate_tool_table(self):

