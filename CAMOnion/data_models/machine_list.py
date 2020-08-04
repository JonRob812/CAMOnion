from CAMOnion.database.tables import *
from PyQt5.QtWidgets import QListWidgetItem

class MachineList:
    def __init__(self, controller):
        self.controller = controller
        self.machines = None
        self.refresh()

    def refresh(self):
        self.machines = self.controller.session.query(Machine).all()

    def add(self, name, max_rpm, spot, drill, tap, peck, ream, countersink, drill_format, tap_format, program_start, program_end,
            tool_start, tool_end, op_start):
        machine = Machine(
            name=name,
            max_rpm=max_rpm,
            spot=spot,
            drill=drill,
            tap=tap,
            peck=peck,
            ream=ream,
            countersink=countersink,
            drill_format=drill_format,
            tap_format=tap_format,
            program_start=program_start,
            program_end=program_end,
            tool_start=tool_start,
            tool_end=tool_end,
            op_start=op_start,
        )

        self.controller.session.add(machine)
        self.controller.session.commit()
        self.refresh()
        return machine

    def delete(self, machine_id):
        machine = self.controller.session.query(Machine).filter(Machine.id == machine_id).one()
        self.controller.session.delete(machine)
        self.controller.session.commit()
        self.refresh()

    @staticmethod
    def safe(name, max_rpm, spot, drill, tap, peck, ream, countersink, drill_format, tap_format, program_start, program_end,
             tool_start, tool_end, op_start):
        try:
            assert len(name) > 1
            assert int(max_rpm) > 0
            for g_code in [spot, drill, tap, peck, ream, countersink]:
                assert int(g_code)
            for code_format in [drill_format, tap_format, program_start, program_end, tool_start, tool_end, op_start]:
                assert len(code_format) > 5
        except:
            print('not safe machine')
            return
        return name, max_rpm, spot, drill, tap, peck, ream, countersink,\
            drill_format, tap_format, program_start, program_end, tool_start, tool_end, op_start

    def safe_add(self, name, max_rpm, spot, drill, tap, peck, ream, countersink, drill_format, tap_format, program_start, program_end, tool_start, tool_end, op_start):
        safe = self.safe(name, max_rpm, spot, drill, tap, peck, ream, countersink, drill_format, tap_format, program_start, program_end, tool_start, tool_end, op_start)
        if safe:
            machine = self.add(*safe)
            return machine

    def safe_edit(self, machine, name, max_rpm, spot, drill, tap, peck, ream, countersink, drill_format, tap_format, program_start, program_end, tool_start, tool_end, op_start):
        safe = self.safe(name, max_rpm, spot, drill, tap, peck, ream, countersink, drill_format, tap_format, program_start, program_end, tool_start, tool_end, op_start)
        if safe:
            machine.name = name
            machine.max_rpm = max_rpm
            machine.spot = spot
            machine.drill = drill
            machine.tap = tap
            machine.peck = peck
            machine.ream = ream
            machine.countersink = countersink
            machine.drill_format = drill_format
            machine.tap_format = tap_format
            machine.program_start = program_start
            machine.program_end = program_end
            machine.op_start = op_start
            machine.tool_start = tool_start
            machine.tool_end = tool_end
            self.controller.session.commit()
            self.refresh()


def populate_machine_combo_widget(widget, machine_list):
    widget.clear()
    for machine in machine_list.machines:
        widget.addItem(MachineListWidgetItem(machine))
    widget.repaint()


class MachineListWidgetItem(QListWidgetItem):
    def __init__(self, machine):
        self.machine = machine
        self.string = f'{machine.name}'
        super().__init__(self.string)


