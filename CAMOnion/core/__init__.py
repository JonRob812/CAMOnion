
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


class Setup:
    def __init__(self, name='New Setup', machine=None, origin=None):
        self.name = name
        self.origin = origin
        self.machine = machine
        self.part_features = []

    def add_feature(self, feature):
        feature.setup = self
        self.part_features.append(feature)


class PartFeature:
    def __init__(self, base_feature_id, setup, geometry=None, parameters=None):
        self.base_feature_id = base_feature_id
        self.setup = setup
        self.geometry = geometry
        if geometry is None:
            self.geometry = [None]
        self.parameters = parameters
        self.part_operations = []

    def add_operation(self, op):
        self.part_operations.append(op)
        op.part_feature = self

    def db_feature(self, session):
        feature = session.query(Feature).filter(Feature.id == self.base_feature_id).one()
        return feature


class PartOperation:
    def __init__(self, base_id, part_feature, tool):
        self.base_id = base_id
        self.part_feature = part_feature
        self.tool = tool











