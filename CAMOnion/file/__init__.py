from datetime import datetime
import pickle
import ezdxf
import copy
from CAMOnion.core import Origin


class CamoFile:
    def __init__(self):
        self.filename = None
        self.can_save = False
        self.date_created = datetime.now()
        self.date_saved = None

        self.active_origin = Origin('Home - G54')

        self.setups = []
        self.origins = []
        self.features = []
        self.operations = []
        self.geometry = []

        self.origins.append(self.active_origin)
        self.dxf_doc = ezdxf.new(ezdxf.DXF2018)

    def set_filename(self, filename):
        self.filename = filename
        self.can_save = True


def save_camo_file(camo_file):
    if camo_file.can_save:
        camo_file.date_saved = datetime.now()
        with open(camo_file.filename, 'wb') as file:
            save_camo = copy.copy(camo_file)
            save_camo.dxf_doc_encoded = save_camo.dxf_doc.encode_base64()
            del save_camo.dxf_doc
            pickle.dump(save_camo, file)
            del save_camo


def open_camo_file(camo_file):
    with open(camo_file, 'rb') as file:
        camo_file = pickle.load(file)
        camo_file.dxf_doc = ezdxf.decode_base64(camo_file.dxf_doc_encoded)
        del camo_file.dxf_doc_encoded
        return camo_file
