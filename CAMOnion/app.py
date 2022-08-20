import os
import sys
from time import sleep
import argparse
import logging

import json


from PyQt5 import QtWidgets as qw
from PyQt5 import QtCore, QtGui


from CAMOnion import stylesheet
from CAMOnion.resources import camo_resources
from CAMOnion.mainwindow import MainWindow
from CAMOnion.databasewindow import databaseWindow
from CAMOnion.connectwindow import ConnectWindow
from CAMOnion.database.db_utils import setup_sql
from CAMOnion.stylesheet import dark
from CAMOnion.data_models.tool_list import ToolList
from CAMOnion.data_models.feature_list import FeatureList
from CAMOnion.data_models.operation_list import OperationList
from CAMOnion.data_models.machine_list import MachineList
from CAMOnion.data_models.file_tree import FileTreeModel, FileTreeNode
from CAMOnion.database.tables import *
from CAMOnion.file import CamoFile, open_camo_file, save_camo_file
from CAMOnion.core import PartFeature, PartOperation
from CAMOnion.core.widget_tools import get_combo_data


from CAMOnion.dialogs.errormessage import show_error_message

organization_name = 'Awesome Blossom'
app_name = 'CAMOnion'
version = '0.1'
icon_file = ':img/icon.ico'

# TODO add remove edit setups and origin and features


class Controller(qw.QApplication):
    def __init__(self, args):
        logging.basicConfig(filename='logging.log', level=logging.DEBUG)
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        self.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        super().__init__(args)
        self.setOrganizationName(organization_name)
        self.setApplicationName(app_name)
        self.setApplicationVersion(version)
        self.setStyleSheet(dark.style)
        self.icon = QtGui.QIcon(icon_file)
        self.tray_icon = qw.QSystemTrayIcon()
        self.tray_icon.setIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.splash = qw.QSplashScreen(QtGui.QPixmap(':img/splash.png'), QtCore.Qt.WindowStaysOnTopHint)

        self.settings = QtCore.QSettings()

        self.db = self.settings.value('db', type=str)
        # self.db = None
        self.sql_connected = self.settings.value('sql_connected', type=bool)
        # self.sql_connected = False
        self.current_camo_file = CamoFile()



        self.engine = None
        self.connection = None
        self.session = None

        self.main_window = None
        self.databaseWindow = None
        self.sql_connect_window = None

        self.tool_list = None
        self.feature_list = None
        self.operation_list = None
        self.machine_list = None
        self.tree_model = None

        self.nc_output = None
        logging.info('end init')

    def launch(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--camo_file')
        parser.add_argument('-no_splash', dest='splash', action='store_false')
        parser.add_argument('file', type=argparse.FileType(), nargs='?')
        args = parser.parse_args()
        if args.splash:
            self.flash_splash()
        if not self.sql_connected:
            self.show_connect_dialog()
        else:
            self.setup_sql()
            self.show_main_window()
            if args.camo_file is not None:
                self.current_camo_file = open_camo_file(args.camo_file)
            elif args.file is not None:
                self.current_camo_file = open_camo_file(args.file.name)
            self.load_camo_file()
        return self.exec_()

    def flash_splash(self):
        self.splash.show()
        sleep(1)
        self.processEvents()
        self.splash.finish(self.main_window)
        # QtCore.QTimer.singleShot(2000, self.splash.finish)

    def show_main_window(self):
        self.main_window = MainWindow(self)
        self.main_window.actionManage_Database.triggered.connect(self.show_database_window)
        self.main_window.actionNew.triggered.connect(self.new_camo_file)
        self.main_window.actionOpen.triggered.connect(self.open_camo_file)
        self.main_window.actionSave.triggered.connect(self.save_camo_file)
        self.main_window.actionSave_as.triggered.connect(self.save_camo_file_as)
        self.main_window.actionSend_Tool_List.triggered.connect(self.send_tool_list)
        self.main_window.actionTake_Picture.triggered.connect(self.take_picture)
        self.main_window.show()

    def show_database_window(self):
        self.databaseWindow = databaseWindow(self)
        self.databaseWindow.show()

    def show_connect_dialog(self):
        self.sql_connect_window = ConnectWindow(self)
        self.sql_connect_window.new_db.connect(self.new_db)
        self.sql_connect_window.show()

    def build_file_tree_model(self):
        self.tree_model = FileTreeModel(self.current_camo_file, self.session)
        self.main_window.treeView.setModel(self.tree_model)
        self.main_window.treeView.setHeaderHidden(True)
        self.main_window.treeView.expandAll()

        self.main_window.treeView.clicked.connect(self.tree_view_clicked)
        self.populate_operation_list()

    def tree_view_clicked(self, index):
        node = index.internalPointer()
        print(node)

    def update_machine(self):
        active_setup = get_combo_data(self.main_window.position_widget.active_setup_combo)

    def populate_operation_list(self):
        self.current_camo_file.operations = []
        active_setup = get_combo_data(self.main_window.position_widget.active_setup_combo)
        features = [feature for feature in self.current_camo_file.features if feature.setup == active_setup]
        for feature in features:
            db_feature = feature.db_feature(self.session)
            for op in db_feature.operations:
                part_op = PartOperation(op, feature)
                self.current_camo_file.operations.append(part_op)
        self.current_camo_file.operations.sort(key=lambda op_: op_.base_operation.camo_op.priority)
        self.populate_op_dock()

    def populate_op_dock(self):
        self.main_window.op_dock.clear()
        for op in self.current_camo_file.operations:
            item = qw.QListWidgetItem(str(op))
            item.op = op
            self.main_window.op_dock.addItem(item)

    def new_db(self, db_url):
        self.db = db_url
        self.setup_sql()
        if self.sql_connected and not self.main_window:
            self.show_main_window()

    def setup_sql(self):
        try:
            engine, connection, session = setup_sql(self.db)
            self.engine = engine
            self.connection = connection
            self.session = session
            self.test_db()
        except:
            show_error_message('Bad SQL URL', 'Please check URL and try again')
            return
        if self.sql_connected:
            self.tool_list = ToolList(self)
            self.feature_list = FeatureList(self)
            self.operation_list = OperationList(self)
            self.machine_list = MachineList(self)

    def test_db(self):
        try:
            _ = self.session.query(Tool_Type).all()
            self.sql_connected = True
            self.settings.setValue('sql_connected', self.sql_connected)
            self.settings.setValue('db', self.db)
        except Exception:
            show_error_message('SQL error', "Invalid SQL URL", qw.QMessageBox.Critical)
            self.show_connect_dialog()

    def new_camo_file(self):
        self.current_camo_file = CamoFile()
        self.load_camo_file()

    def load_camo_file(self):
        self.build_file_tree_model()
        self.main_window.set_document(self.current_camo_file.dxf_doc)
        self.main_window.populate_origin_comboBox()
        self.main_window.populate_active_setup_combo()

    def get_camo_filename(self):
        filename, _ = qw.QFileDialog.getOpenFileName(self.main_window, 'Select .camo File', filter='*.camo')
        return filename

    def open_camo_file(self):
        filename = self.get_camo_filename()
        if filename == '':
            return
        self.current_camo_file = open_camo_file(filename)
        if not hasattr(self.current_camo_file, 'setups'):
            self.current_camo_file.setups = []
        self.load_camo_file()

    def save_camo_file(self):
        filename = self.current_camo_file.filename
        if not filename:
            filename, _ = qw.QFileDialog.getSaveFileName(self.main_window, 'Save new *.camo file', filter='*.camo')
            if filename == '':
                pass
            else:
                self.current_camo_file.set_filename(filename)
        print(filename)
        save_camo_file(self.current_camo_file)

    def save_camo_file_as(self):
        filename, _ = qw.QFileDialog.getSaveFileName(self.main_window, 'Save as *.camo file', filter='*.camo')
        self.current_camo_file.set_filename(filename)
        self.save_camo_file()

    def send_tool_list(self):
        self.populate_operation_list()
        self.tool_list = list(set([op.base_operation.tool for op in self.current_camo_file.operations]))
        self.tool_list.sort(key=lambda t: t.tool_number)
        if len(self.tool_list) > 0:
            try:
                setup_id = self.current_camo_file.operations[0].part_feature.setup.qb_setup_id

                column_list = '6.12.9'
                csv = "".join([f"{tool.tool_number}, {tool.qb_id}, {setup_id}\n"
                               for tool in self.tool_list])
                purge_response = self.qb_client.purgerecords(query=f'{{9.TV.{setup_id}}}', database='bnmac5wdg')
                import_response = self.qb_client.importfromcsv(recordscsv=csv, database='bnmac5wdg', clist=column_list,
                                                               skipfirst=False)
                response = [purge_response, import_response]
                self.main_window.info.clear()
                pretty_response = json.dumps(response, indent=2)
                for line in pretty_response.splitlines():
                    self.main_window.info.append(str(line))
            except:
                show_error_message('No Setup ID', 'Enter valid setup ID')
                return
        else:
            show_error_message('No Tools', "please add something to get tools from")

    def take_picture(self):
        path, _ = qw.QFileDialog.getSaveFileName(self.main_window, caption='Save Image', filter='jpeg Documents (*.jpeg)')
        if path:
            image = self.main_window.view.grab(self.main_window.view.viewport().rect())
            image = image.scaledToHeight(5000)
            image.save(path)

