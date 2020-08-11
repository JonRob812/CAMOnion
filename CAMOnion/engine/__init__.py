from CAMOnion.database.tables import *


def post(operations, session):
    code = []
    machine = session.query(Machine).filter(Machine.id == operations[0].part_feature.setup.machine_id).one()
    origin = operations[0].part_feature.setup.origin
    print(machine, origin)
    for op in operations:
        print(op)


