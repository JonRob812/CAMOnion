import math


def face_rough(op):
    op.tool_path = []
    x_positive = True
    step_over = float(op.base_operation.tool.diameter) * .9
    part_width = abs(op.points[0][1] - op.points[1][1])
    number_of_passes = math.ceil(((part_width - step_over) / step_over))
    step_over = part_width / number_of_passes
    x_left = round(op.points[0][0] - float(op.base_operation.tool.diameter) * 1.2, 4)
    x_right = round(op.points[1][0] + float(op.base_operation.tool.diameter) * 1.2, 4)

    for i in range(number_of_passes):
        y_corner = op.points[0][1] + step_over / 2
        if x_positive:
            point = (x_left, round(y_corner - ((i + 1) * step_over), 4))
            op.tool_path.append(point)
            point = (x_right, round((y_corner - ((i + 1) * step_over)), 4))
            op.tool_path.append(point)
        else:
            point = (x_right, round((y_corner - ((i + 1) * step_over)), 4))
            op.tool_path.append(point)
            point = (x_left, round((y_corner - ((i + 1) * step_over)), 4))
            op.tool_path.append(point)
        x_positive = not x_positive

    code = [f"G01 Z.015 F{float(op.base_operation.fixed_feed(op.part_feature.setup.machine.max_rpm)):.2f}"]
    for point in op.tool_path:
        code.append(f'G01 X{point[0]} Y{point[1]}')
    code.append(f'G00 Z{op.part_feature.setup.clearance_plane:.2f}')
    return '\n'.join(code)


def face_finish(op):
    op.tool_path = []
    y_negative = True
    step_over = float(op.base_operation.tool.diameter) * .9
    part_width = abs(op.points[0][0] - op.points[1][0])
    number_of_passes = math.ceil(((part_width - step_over) / step_over))
    step_over = part_width / number_of_passes
    y_up = round(op.points[0][1] + float(op.base_operation.tool.diameter) * .6, 4)
    y_down = round(op.points[1][1] - float(op.base_operation.tool.diameter) * .6, 4)

    for i in range(number_of_passes):
        x_corner = op.points[0][0] - step_over / 2
        if y_negative:
            point = (round(x_corner + ((i + 1) * step_over), 4), y_up)
            op.tool_path.append(point)
            point = (round((x_corner + ((i + 1) * step_over)), 4), y_down)
            op.tool_path.append(point)
        else:
            point = (round((x_corner + ((i + 1) * step_over)), 4), y_down)
            op.tool_path.append(point)
            point = (round((x_corner + ((i + 1) * step_over)), 4), y_up)
            op.tool_path.append(point)
        y_negative = not y_negative

    code = [f"G01 Z0 F{float(op.base_operation.fixed_feed(op.part_feature.setup.machine.max_rpm)):.2f}"]
    for point in op.tool_path:
        code.append(f'G01 X{point[0]} Y{point[1]}')
    code.append(f'G00 Z{op.part_feature.setup.clearance_plane:.2f}')
    return '\n'.join(code)
