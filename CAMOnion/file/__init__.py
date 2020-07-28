from datetime import datetime
import pickle


class CamoFile:
    def __init__(self):
        self.filename = None
        self.can_save = False
        self.date_created = datetime.now()
        self.date_saved = None

        self.geometry = []
        self.features = []
        self.operations = []
        self.dxf_imports = []

    def set_filename(self, filename):
        self.filename = filename
        self.can_save = True


def save(camo_file):
    if camo_file.can_save:
        camo_file.date_saved = datetime.now()
        with open(camo_file.filename, 'wb') as file:
            pickle.dump(camo_file, file)


def open_camo_file(camo_file):
    with open(camo_file, 'rb') as file:
        return pickle.load(file)
