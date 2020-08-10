from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
import typing

from CAMOnion.core import CamoItemTypes as ct


class FileTreeNode(object):
    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, "__getitem__"):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

        self.type = None

    def data(self, column):
        if 0 <= column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if 0 <= row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True


class FileTreeModel(QAbstractItemModel):

    def __init__(self, camo_file, session):
        super().__init__()
        self.session = session
        self.origin_index = None
        self.setup_index = None
        self.geo_index = None
        self.indexes = {}

        self._root = FileTreeNode(None)
        origins_node = FileTreeNode('Origins')
        setups_node = FileTreeNode('Setups')
        geo_node = FileTreeNode('Geometry')

        self._root.addChild(setups_node)
        self._root.addChild(origins_node)
        self._root.addChild(geo_node)

        for origin in camo_file.origins:
            origin_node = FileTreeNode((origin.name, origin))
            origin_node.type = ct.OOrigin
            origins_node.addChild(origin_node)

        for setup in camo_file.setups:
            features = [feature for feature in camo_file.features if feature.setup == setup]
            setup_node = FileTreeNode((setup.name, setup))
            setup_node.type = ct.OSetup
            setups_node.addChild(setup_node)

            for feature in features:
                feature_node = FileTreeNode((feature.db_feature(self.session).name, feature))
                feature_node.type = ct.OFeature
                setup_node.addChild(feature_node)

        geo_entities = camo_file.dxf_doc.modelspace().entity_space.entities

        for entity in geo_entities:
            entity_node = FileTreeNode((str(entity), entity))
            entity_node.type = ct.ODXF
            geo_node.addChild(entity_node)

    def index(self, row, column, parent_index=None):
        if not parent_index:
            parent_index = QModelIndex()
        if not parent_index.isValid():
            parent = self._root
        else:
            parent = parent_index.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, parent_index):
            return QModelIndex()

        if child := parent.child(row):
            index = QAbstractItemModel.createIndex(self, row, column, child)
            if 'Geometry' in child._data:
                self.geo_index = index
            if 'Setups' in child._data:
                self.setup_index = index
            if hasattr(child, 'entity'):
                self.indexes[str(child.entity)] = index
            return index
        else:
            return QModelIndex()

    def parent(self, index):
        if index.isValid():
            if p := index.internalPointer().parent():
                return QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QModelIndex()

    def rowCount(self, parent_index=None):
        if parent_index and parent_index.isValid():
            return parent_index.internalPointer().childCount()
        return self._root.childCount()

    def columnCount(self, index=None):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index=None, role=None):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            return node.data(index.column())
        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.isValid() and role == Qt.EditRole:
            node = index.internalPointer()
            node._data[index.column()] = value
            row = index.row()
            column = index.column()

            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.isValid():
            node = index.internalPointer()
            flags = Qt.ItemIsEnabled
            if node.childCount() == 0:
                flags |= Qt.ItemIsSelectable
                return flags
        return super(FileTreeModel, self).flags(index)

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if not parent.isValid():
            # parent is not valid when it is the root node, since the "parent"
            # method returns an empty QModelIndex
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()  # the node

        parentNode.removeChild(row)
        return True


