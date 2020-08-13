import math


def slot_rough(op):
    op.tool_path = []
    code = []
    for slot in op.points:
        x_1, y_1 = slot[0][0], slot[0][1]
        x_2, y_2 = slot[1][0], slot[1][1]
        length = math.sqrt(abs(x_1 - x_2) ** 2 + abs(y_1 - y_2) ** 2)
        depth = float(op.part_feature.depths[op.base_operation.camo_op.op_type])
        ramp_depth = length * math.tan(1 * math.pi / 180)
        start_point = (x_1, y_1)
        flippy_floppy = False
        number_of_passes = math.ceil(abs(depth) / ramp_depth)
        ramp_depth = depth / number_of_passes
        temp_path = []
        for i in range(number_of_passes):
            if flippy_floppy:
                temp_path.append((x_1, y_1, (i + 1) * ramp_depth))
            else:
                temp_path.append((x_2, y_2, (i + 1) * ramp_depth))
            flippy_floppy = not flippy_floppy
        if flippy_floppy:
            temp_path.append((x_1, y_1, depth))
        else:
            temp_path.append((x_2, y_2, depth))
        op.tool_path.append((start_point, temp_path))
    for slot_path in op.tool_path:
        start_point = slot_path[0]
        tool_path = slot_path[1]
        code.append(f"G00 X{round(start_point[0],4)} Y{round(start_point[1],4)}")
        code.append(f"G01 Z0 F{op.base_operation.feed:.2f}")
        for point in tool_path:
            code.append(f"X{round(point[0],4)} Y{round(point[1], 4)} Z{round(point[2], 4)}")
        code.append(f"G00 Z{op.part_feature.setup.clearance_plane:.2f}")
    return '\n'.join(code)


def slot_finish(op):
    op.tool_path = []
    for slot in op.points:
        op.tool_path.append([(slot[0][0], slot[0][1]), (slot[1][0], slot[1][1])])
    code = []
    for slot in op.tool_path:
        start_point = slot[0]
        code.append(f"G00 X{round(start_point[0], 4)} Y{round(start_point[1], 4)}")
        code.append(f"G01 Z0 F{op.base_operation.feed:.2f}")
        for point in slot:
            code.append(f"X{point[0]} Y{point[1]} Z{op.part_feature.depths[op.base_operation.camo_op.op_type]}")
        code.append("G00 Z.1")
    return '\n'.join(code)
