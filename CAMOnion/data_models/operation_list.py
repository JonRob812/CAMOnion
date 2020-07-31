from CAMOnion.database.tables import *


class OperationList:
    def __init__(self, controller):
        self.controller = controller
        self.operations = None
        self.types = None
        self.refresh()

    def refresh(self):
        self.operations = self.controller.session.query(Operation).all()
        self.types = self.controller.session.query(CamoOp).all()

    def add(self, feature, tool, camo_op, feed, speed, peck=0):
        op = Operation(
            feature_id=feature.id,
            tool_id=tool.id,
            camo_op_id=camo_op.id,
            feed=feed, speed=speed,
            peck=peck)
        self.controller.session.add(op)
        self.controller.session.commit()
        self.refresh()
        return op

    @staticmethod
    def safe(feature, tool, camo_op, feed, speed, peck):
        if peck == '':
            peck = 0
        try:
            assert isinstance(feature, Feature)
            assert isinstance(tool, Tool)
            assert isinstance(camo_op, CamoOp)
            assert float(feed) > 0
            assert int(speed) > 0
            assert float(peck) >= 0
        except:
            print('bad op')
            return
        return feature, tool, camo_op, float(feed), int(speed), float(peck)

    def safe_edit(self, op, feature, tool, camo_op, feed, speed, peck):
        this_is_safe = self.safe(feature, tool, camo_op, feed, speed, peck)
        if this_is_safe:
            op.feature_id = feature.id
            op.tool_id = tool.id
            op.camo_op_id = camo_op.id
            op.feed = feed
            op.speed = speed
            op.peck = peck
            self.controller.session.commit()
            self.refresh()

    def safe_add(self, feature, tool, camo_op, feed, speed, peck):
        safe = self.safe(feature, tool, camo_op, feed, speed, peck)
        if safe:
            op = self.add(*safe)
            return op

    def delete(self, op_id):
        op = self.controller.session.query(Operation).filter(Operation.id == op_id).one()
        self.controller.session.delete(op)
        self.controller.session.commit()
        self.refresh()
