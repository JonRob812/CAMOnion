
class VirtualMachine:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.s = 0
        self.f = 0
        self.tool = None
        self.position = {}
        self.last_move = {'x': 0,
                          'y': 0,
                          'z': 0}
        self.update_position()

    def update_position(self):
        self.position = {'x': self.x,
                         'y': self.y,
                         'z': self.z}

    def move_to(self, x, y, z):
        self.last_move['x'] = x - self.x
        self.last_move['y'] = y - self.y
        self.last_move['z'] = z - self.z
        self.x = x
        self.y = y
        self.z = z
        self.update_position()
        return self.last_move

    def get_position(self):
        self.update_position()
        return self.position
