
from CAMOnion.database.tables import *


class CamoItemTypes:
    OOrigin = 0
    OSetup = 1
    OFeature = 2
    OOp = 3
    ODXF = 4


class Origin:
    def __init__(self, name, wfo_num=0, x=0.0, y=0.0, angle=0.0):
        self.name = name
        self.wfo_num = wfo_num
        self.x = x
        self.y = y
        self.angle = angle

    def __str__(self):
        return f'origin: {self.name} G{self.wfo_num + 54} X{self.x} Y{self.y} angle:{self.angle}'

class Setup:
    def __init__(self, name='New Setup', machine_id=None, origin=None, clearance_plane=1.0):
        self.name = name
        self.origin = origin
        self.machine_id = machine_id
        self.clearance_plane = clearance_plane


class PartFeature:
    def __init__(self, base_feature_id, setup, geometry=None, depths=None):
        self.base_feature_id = base_feature_id
        self.setup = setup
        self.geometry = geometry
        self.depths = depths
        if geometry is None:
            self.geometry = [None]

    def db_feature(self, session):
        feature = session.query(Feature).filter(Feature.id == self.base_feature_id).one()
        return feature

    def __str__(self):
        string = f'{self}'


class PartOperation:
    def __init__(self, base_operation, part_feature):
        self.base_operation = base_operation
        self.part_feature = part_feature

    def __str__(self):
        string = f'{self.base_operation.feature.name} ' \
                 f'{self.base_operation.camo_op.feature_type.feature_type} ' \
                 f'{self.base_operation.camo_op.function} ' \
                 f'{self.base_operation.tool.diameter} ' \
                 f'{self.base_operation.tool.name} ' \
                 f'qty {len(self.part_feature.geometry)}'
        return string













