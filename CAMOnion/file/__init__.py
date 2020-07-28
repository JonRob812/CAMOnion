from datetime import datetime
import pickle
import ezdxf


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
        self.dxf_doc = ezdxf.new(ezdxf.DXF2010)
        self.dxf_doc_msp = self.dxf_doc.modelspace()
        self.dxf_doc.modelspace()

    def set_filename(self, filename):
        self.filename = filename
        self.can_save = True


def save(camo_file):
    if camo_file.can_save:
        camo_file.date_saved = datetime.now()
        with open(camo_file.filename, 'wb') as file:
            camo_file.dxf_doc_encoded = camo_file.dxf_doc.encode_base64()
            del camo_file.dxf_doc
            del camo_file.dxf_doc_msp
            pickle.dump(camo_file, file)



def open_camo_file(camo_file):
    with open(camo_file, 'rb') as file:
        camo_file = pickle.load(file)
        camo_file.dxf_doc = ezdxf.decode_base64(camo_file.dxf_doc_encoded)
        del camo_file.dxf_doc_encoded
        return camo_file
