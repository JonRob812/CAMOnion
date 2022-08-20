from CAMOnion.database.tables import *
from CAMOnion.core.math_tools import rotate_point
from CAMOnion.engine import face, slot, drill
import os

code_engines = {
    'face_rough': face.face_rough,
    'face_finish': face.face_finish,
    'slot_rough': slot.slot_rough,
    'slot_finish': slot.slot_finish,
    'drill': drill.drill,
}


class CodeBuilder:
    def __init__(self, controller):
        self.controller = controller
        self.operations = self.controller.current_camo_file.operations
        self.session = self.controller.session
        self.setup = self.operations[0].part_feature.setup
        self.machine = self.session.query(Machine).filter(
            Machine.id == self.operations[0].part_feature.setup.machine_id).one()
        self.origin = self.setup.origin
        self.header_comment = os.path.basename(self.controller.current_camo_file.filename)
        self.program_number = self.operations[0].part_feature.setup.program_number

        self.dxf_entities = self.controller.main_window.all_dxf_entities

        self.tool_set = set()
        self.tool_list = []
        self.code = []
        self.current_tool = None
        self.next_tool = None
        self.get_tool_list()
        self.process_operations()

    def process_operations(self):
        for i, op in enumerate(self.operations):
            print('op')
            # if int(op.base_operation.speed) > int(op.part_feature.setup.machine.max_rpm):
            #     op.base_operation.feed = float(op.base_operation.feed) * (
            #                 int(op.part_feature.setup.machine.max_rpm) / int(op.base_operation.speed))
            #     op.base_operation.speed = int(op.part_feature.setup.machine.max_rpm)
            op.machine = self.machine
            op.points = self.get_operation_points(op)
            op.cutting_code = code_engines[op.base_operation.camo_op.function](op)
            op.start_code = self.get_start_code(op, i)
            op.end_code = self.get_end_of_tool_code()

    def get_start_code(self, op, i):
        code = []
        spindle = get_spindle(op)
        x, y = set_start_location(op)
        if self.current_tool != op.base_operation.tool.tool_number:
            self.get_tool_start_code(code, op, spindle, x, y)
        else:
            self.get_op_start_code(code, op, spindle)
        self.set_current_tool(op, i)
        return ''.join(code)

    def set_current_tool(self, op, i):
        self.current_tool = op.base_operation.tool.tool_number
        if i < len(self.operations) - 1:
            self.next_tool = self.operations[i + 1].base_operation.tool.tool_number
        if i == len(self.operations) - 1:
            self.next_tool = self.operations[0].base_operation.tool.tool_number

    def get_tool_start_code(self, code, op, spindle, x, y):
        code.append(self.machine.tool_start.format
                    (tool_name=f"{op.base_operation.tool.name}",
                     work_offset=op.part_feature.setup.origin.wfo_num + 54,
                     x=round(x, 4),
                     y=round(y, 4),
                     spindle=spindle,
                     tool_number=op.base_operation.tool.tool_number,
                     clearance=op.part_feature.setup.clearance_plane,
                     next_tool=self.next_tool,
                     coolant='M8'))

    def get_op_start_code(self, code, op, spindle):
        code.append(self.machine.op_start.format
                    (x=round(op.points[0][0], 4),
                     y=round(op.points[0][1], 4),
                     spindle=spindle,
                     clearance=op.part_feature.setup.clearance_plane))

    def get_end_of_tool_code(self):
        code = []
        if self.next_tool and self.next_tool != self.current_tool:
            code.append(self.machine.tool_end)
        if len(code) > 0:
            return ''.join(code)
        else:
            return ''

    def get_tool_list(self):
        self.tool_list = list(set([op.base_operation.tool for op in self.operations]))
        self.tool_list.sort(key=lambda t: t.tool_number)
        string_builder = ''
        for tool in self.tool_list:
            string_builder += f'(T{tool.tool_number} - {tool.name})\n'
        self.tool_list = string_builder[:-1]

    def get_operation_points(self, op):
        points = []
        if op.base_operation.feature.feature_type.id == 3:  # facing
            points = self.get_face_points()
        elif op.base_operation.feature.feature_type.id == 1:  # drilling
            points = self.get_drill_points(op)
        elif op.base_operation.feature.feature_type.id == 2:  # slotting
            points = self.get_slot_points(op)

        return points

    def post(self):

        self.code = []

        self.get_program_start_code()
        self.get_code_body()
        self.get_program_end_code()

        for i, line in enumerate(self.code):
            print(line)
            if line == '':
                self.code.pop(i)
        return '\n'.join(self.code)

    def get_program_start_code(self):
        self.code.append(self.machine.program_start.format
                         (program_number=self.program_number,
                          program_comment=self.header_comment.upper(),
                          tool_list=self.tool_list,
                          machine_name=self.machine.name.upper()))

    def get_code_body(self):
        for op in self.operations:
            self.code.append(op.start_code)
            self.code.append(op.cutting_code)
            self.code.append(op.end_code)

    def get_program_end_code(self):
        self.code.append(self.machine.program_end)

    def get_slot_points(self, op):
        op_geo = [self.dxf_entities[entity] for entity in op.part_feature.geometry]
        points = all_slot_points_from_lines(op_geo)
        rotated_lines = []
        for line in points:
            rotated_line_points = []
            for point in line:
                rotated_line_points.append(self.translate_point(point))
            rotated_lines.append((rotated_line_points[0], rotated_line_points[1]))
        return rotated_lines

    def get_drill_points(self, op):
        op_geo = [self.dxf_entities[entity] for entity in op.part_feature.geometry]
        points = [self.translate_point((round(entity.dxf.center.x, 4), round(entity.dxf.center.y, 4))) for entity in
                  op_geo]
        return zig_zag(points)

    def get_face_points(self):
        all_lines = [self.dxf_entities[entity] for entity in self.dxf_entities if
                     self.dxf_entities[entity].DXFTYPE == 'LINE']
        all_points = all_points_from_lines(all_lines)
        x_left = min(map(lambda point: point[0], all_points))
        x_right = max(map(lambda point: point[0], all_points))
        y_top = max(map(lambda point: point[1], all_points))
        y_bottom = min(map(lambda point: point[1], all_points))
        points = [self.translate_point((x_left, y_top)), self.translate_point((x_right, y_bottom))]
        return points

    def translate_point(self, point):
        x, y = point
        shifted_point = (x - self.origin.x, y - self.origin.y)
        rotated_point = rotate_point(shifted_point, -self.origin.angle)
        return rotated_point


def all_points_from_lines(lines):
    points = []
    for line in lines:
        points.append(line.dxf.start)
        points.append(line.dxf.end)
    return points


def all_slot_points_from_lines(lines):
    points = []
    for line in lines:
        points.append(((round(line.dxf.start[0], 4), round(line.dxf.start[1], 4)),
                       (round(line.dxf.end[0], 4), round(line.dxf.end[1], 4))))
    return points


def get_spindle(op):
    if op.base_operation.camo_op.op_type == 'Tap':
        return ''
    else:
        return f"M3 S{int(op.base_operation.fixed_speed(op.machine.max_rpm))}"


def set_start_location(op):
    function = op.base_operation.camo_op.function
    if 'slot' in function:
        return op.points[0][0][0], op.points[0][0][1]
    elif 'drill' in function or 'tap' in function:
        return op.points[0][0], op.points[0][1]
    elif 'face' in function:
        return op.tool_path[0][0], op.tool_path[0][1]


def zig_zag(points):  # "set" gets unique values, "map" is for using function on list
    values = sorted(list(set(map(lambda x: x[0], points))))
    new_points = []
    rev = False
    for v in values:
        li = [x for x in points if x[0] == v]
        new_points += sorted(li, key=lambda tup: tup[1], reverse=rev)
        rev = not rev
    return new_points
