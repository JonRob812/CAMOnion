
def drill(op):
    g = op.part_feature.setup.machine.__dict__[op.base_operation.camo_op.op_type.lower()]
    if g == '83':
        g = f'{g} Q{op.part_feature.setup.machine.__dict__["peck"]}'
    remaining_points = op.points[1:]
    canned_points = '\n'.join([f'X{point[0]:.4f} Y{point[1]:.4f}' for point in remaining_points])
    points = canned_points
    if op.base_operation.camo_op.op_type == 'Tap':
        code_format = 'tap_format'
        p = float(op.base_operation.tool.pitch)
        if float(p) < 4:
            p = float(p) / 25.4
        else:
            p = round(1 / float(op.base_operation.tool.pitch), 4)
        d = op.part_feature.depths[op.base_operation.camo_op.op_type]
        s = str(int(op.base_operation.speed))
        f = round(float(p) * float(s),4)
    elif op.base_operation.camo_op.op_type == 'Ream':
        code_format = 'drill_format'
        d = op.part_feature.depths['Ream']
        f = op.base_operation.feed
        p = None
        s = None
    elif op.base_operation.camo_op.op_type == 'Countersink':
        code_format = 'drill_format'
        d = op.part_feature.depths[op.base_operation.camo_op.op_type]
        f = op.base_operation.feed
        p = None
        s = None
    else:  # must be a Drill
        code_format = 'drill_format'
        d = op.part_feature.depths[op.base_operation.camo_op.op_type]
        f = op.base_operation.feed
        p = None
        s = None
    if f is not None:
        f = str(round(float(f), 2))
    if p is not None:
        p = str(round(float(p), 4))
    return op.part_feature.setup.machine.__dict__[code_format].format(code=g, depth=d, r_plane=.1, speed=s, feed=f, pitch=p,
                                                      points=points, )
