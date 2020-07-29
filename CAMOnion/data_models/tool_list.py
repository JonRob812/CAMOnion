from CAMOnion.database.tables import *


class ToolList:
    def __init__(self, controller):
        self.controller = controller
        self.tools = None
        self.types = None
        self.refresh()

    def refresh(self):
        self.tools = self.controller.session.query(Tool).join(Tool_Type).all()
        self.types = self.controller.session.query(Tool_Type).all()

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
        self.controller.session.add(tool)
        self.controller.session.commit()
        self.refresh()

    def delete(self, tool_id):
        tool = self.controller.session.query(Tool).filter(Tool.id == tool_id).one
        self.controller.session.delete(tool)
        self.controller.session.commit()
        self.refresh()



