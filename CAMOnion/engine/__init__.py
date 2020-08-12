from CAMOnion.database.tables import *
from CAMOnion.core.math_tools import rotate_point
import os

def post(operations, session):
    code = []
    setup = operations[0].part_feature.setup
    machine = session.query(Machine).filter(Machine.id == operations[0].part_feature.setup.machine_id).one()
    origin = setup.origin
    print(machine, origin)
    for op in operations:
        print(op)


class CodeBuilder:
    def __init__(self, controller):
        self.controller = controller
        self.operations = self.controller.current_camo_file.operations
        self.session = self.controller.session
        self.setup = self.operations[0].part_feature.setup
        self.machine = self.session.query(Machine).filter(Machine.id == self.operations[0].part_feature.setup.machine_id).one()
        self.origin = self.setup.origin
        self.header_comment = os.path.basename(self.controller.current_camo_file.filename)

        self.dxf_entities = self.controller.main_window.all_dxf_entities

        self.tool_list = None
        self.code = []
        self.current_tool = None
        self.next_tool = None
        self.process_operations()

    def process_operations(self):
        for op in self.operations:
            print(op)
            op.points = self.get_operation_points(op)

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

        for line in self.code:
            print(line)

    def get_program_start_code(self):
        self.code.append(self.machine.program_start.format(program_number=100, program_comment=self.header_comment,
                                                           tool_list=self.tool_list))

    def get_code_body(self):
        pass

    def get_slot_points(self, op):
        op_geo = [self.dxf_entities[entity] for entity in op.part_feature.geometry]
        points = all_slot_points_from_lines(op_geo)
        translated_points = []
        for line in points:

            for point in line:
                translated_points.append(self.translate_point(point))

        return (translated_points[0], translated_points[1]), (translated_points[2], translated_points[3])

    def get_drill_points(self, op):
        op_geo = [self.dxf_entities[entity] for entity in op.part_feature.geometry]
        points = [self.translate_point((entity.dxf.center.x, entity.dxf.center.y)) for entity in op_geo]
        return points

    def get_face_points(self):
        all_lines = [self.dxf_entities[entity] for entity in self.dxf_entities if self.dxf_entities[entity].DXFTYPE == 'LINE']
        all_points = all_points_from_lines(all_lines)
        x_left = min(map(lambda point: point[0], all_points))
        x_right = max(map(lambda point: point[0], all_points))
        y_top = max(map(lambda point: point[1], all_points))
        y_bottom = min(map(lambda point: point[1], all_points))
        points = [self.translate_point((x_left, y_top)), self.translate_point((x_right, y_bottom))]
        return points

    def get_program_end_code(self):
        pass

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
        points.append(((line.dxf.start[0], line.dxf.start[1]), (line.dxf.end[0], line.dxf.end[1])))
    return points

