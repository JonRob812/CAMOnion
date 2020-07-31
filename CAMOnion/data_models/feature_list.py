from CAMOnion.database.tables import *


class FeatureList:
    def __init__(self, controller):
        self.controller = controller
        self.features = None
        self.types = None
        self.refresh()

    def refresh(self):
        self.features = self.controller.session.query(Feature).all()
        self.types = self.controller.session.query(Feature_Type).all()

    def add(self, name, desc, type_id):
        feature = Feature(name=name, description=desc, feature_type_id=type_id)
        self.controller.session.add(feature)
        self.controller.session.commit()
        self.refresh()
        return feature

    def add_from_dict(self, f_dict):
        f = self.add(f_dict['name'], f_dict['desc'], f_dict['type_id'])
        return f

    def get_valid_feature_dict(self, name, desc, type_id):
        if name not in [feature.name for feature in self.features] or name != '':
            feature_dict = {
                'name': name,
                'desc': desc,
                'type_id': type_id
            }
            return feature_dict

    def delete(self, f_id):
        feature = self.controller.session.query(Feature).filter(Feature.id == f_id).one()
        self.controller.session.delete(feature)
        self.controller.session.commit()
        self.refresh()





