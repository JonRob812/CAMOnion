from CAMOnion.ui.camo_setup_dialog_ui import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore as qc


class SetupDialog(QDialog, Ui_Dialog):

    def __init__(self, controller):
        super().__init__()
        self.setupUi(self)
        self.controller = controller
        for machine in controller.machine_list.machines:
            self.machine_combo.addItem(machine.name, machine)

        for origin in controller.current_camo_file.origins:
            self.origin_combo.addItem(origin.name, origin)

