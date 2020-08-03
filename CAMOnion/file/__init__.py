from datetime import datetime
import pickle
import ezdxf


class CamoFile:
    def __init__(self):
        self.filename = None
        self.can_save = False
        self.date_created = datetime.now()
        self.date_saved = None

        self.setups = []
        self.origins = []
        self.features = []
        self.operations = []
        self.geometry = []

        self.dxf_imports = []
        self.dxf_doc = ezdxf.new(ezdxf.DXF2018)

    def set_filename(self, filename):
        self.filename = filename
        self.can_save = True


def save(camo_file):
    if camo_file.can_save:
        camo_file.date_saved = datetime.now()
        with open(camo_file.filename, 'wb') as file:
            camo_file.dxf_doc_encoded = camo_file.dxf_doc.encode_base64()
            del camo_file.dxf_doc
            pickle.dump(camo_file, file)
            camo_file.dxf_doc = ezdxf.decode_base64(camo_file.dxf_doc_encoded)


def open_camo_file(camo_file):
    with open(camo_file, 'rb') as file:
        camo_file = pickle.load(file)
        camo_file.dxf_doc = ezdxf.decode_base64(camo_file.dxf_doc_encoded)
        del camo_file.dxf_doc_encoded
        msp = camo_file.dxf_doc.modelspace()
        return camo_file
