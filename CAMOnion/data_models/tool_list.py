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
        tool_ids = [int(x.qb_id) for x in self.tools]
        if int(qb_id) not in tool_ids:
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
            print(tool)
            return tool

    def add_from_dict(self, tool_dict):
        diameter = tool_dict['diameter']
        tool_number = tool_dict['tool_number']
        tool_type_id = tool_dict['tool_type_id']
        name = tool_dict['name']
        qb_id = tool_dict['qb_id']
        num_flutes = tool_dict['num_flutes']
        pitch = tool_dict['pitch']
        tool = self.add(diameter, tool_number, tool_type_id, name=name, qb_id=qb_id, num_flutes=num_flutes, pitch=pitch)
        print(tool)
        return tool

    @staticmethod
    def get_valid_tool_dict(dia, num, t_id, name, qb_id, flutes, pitch):
        try:
            tool_dict = {'diameter': dia,
                         'tool_number': num,
                         'tool_type_id': t_id,
                         'name': name,
                         'qb_id': qb_id,
                         'num_flutes': flutes,
                         'pitch': pitch
                         }
            assert float(tool_dict['diameter']) > 0
            assert int(tool_dict['tool_number']) > 0
            assert int(tool_dict['tool_type_id']) > 0
            assert len(tool_dict['name']) > 1
            assert int(tool_dict['qb_id']) > 0
            assert int(tool_dict['num_flutes']) > 0
            assert float(tool_dict['pitch']) >= 0
        except:
            return None
        return tool_dict

    def delete(self, tool_id):
        tool = self.controller.session.query(Tool).filter(Tool.id == tool_id).one()
        self.controller.session.delete(tool)
        self.controller.session.commit()
        self.refresh()
