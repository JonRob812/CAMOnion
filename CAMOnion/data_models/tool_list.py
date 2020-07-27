from CAMOnion.database.tables import *


class ToolList:
    def __init__(self, session):
        self.session = session
        self.tools = None
        self.refresh()

    def refresh(self):
        self.tools = self.session.query(Tool).all()

    def add(self, diameter, tool_number, tool_type_id, name=None, qb_id=None, num_flutes=0, pitch=0):
        tool = Tool(
            qb_id=qb_id,
            tool_type_id=tool_type_id,
            tool_number=tool_number,
            name=name,
            diameter=diameter,
            number_of_flutes=num_flutes,
            pitch=pitch
        )
        self.session.add(tool)
        self.session.commit()
        self.refresh()

    def delete(self, tool_id):
        tool = self.session.query(Tool).filter(Tool.id == tool_id).one
        self.session.delete(tool)
