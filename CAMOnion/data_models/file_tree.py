from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
import typing


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

    def data(self, column):
        print(f'calling node data column:{column}')
        if 0 <= column < len(self._data):
            return self._data[column]

    def columnCount(self):
        print(self.data, 'node calling column count')
        return self._columncount

    def childCount(self):
        print(self._data, 'node child count')
        return len(self._children)

    def child(self, row):
        print(self._data, 'node child row', row)
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


class FileTreeModel(QAbstractItemModel):

    def __init__(self, camo_file):
        super().__init__()
        self.indexes = {}

        self._root = FileTreeNode(None)

        setups_node = FileTreeNode('Setups')

        self._root.addChild(setups_node)

        for i, setup in enumerate(camo_file.setups):
            setups_node.addChild(setup)

        geo_node = FileTreeNode('Geometry')
        self._root.addChild(geo_node)
        msp = camo_file.dxf_doc.modelspace()
        geo_entities = camo_file.dxf_doc.modelspace().entity_space.entities

        for i, entity in enumerate(geo_entities):
            entity_node = FileTreeNode(str(entity))
            entity_node.entity = entity
            geo_node.addChild(entity_node)
            # index = self.createIndex(entity_node.row(), 0, geo_node)
            # print(index.data(), index.row())

    def index(self, row, column, parent_index=None):
        print(f'calling index row{row}, col{column}, parent_index={parent_index}')
        if not parent_index:
            parent_index = QModelIndex()
        if not parent_index.isValid():
            parent = self._root
        else:
            parent = parent_index.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, parent_index):
            print('return 1')
            return QModelIndex()

        if child := parent.child(row):
            print('return 2')
            index = QAbstractItemModel.createIndex(self, row, column, child)
            print(index.internalPointer())
            if 'Geometry' in child._data:
                self.geo_index = index
            if hasattr(child, 'entity'):
                self.indexes[str(child.entity)] = index

            return index
        else:
            print('return 3')
            return QModelIndex()

    def parent(self, index):
        print('parent called, index', index.internalPointer())
        if index.isValid():
            if p := index.internalPointer().parent():
                return QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QModelIndex()

    def rowCount(self, parent_index=None):
        print('index pointer', parent_index.internalPointer())
        if parent_index and parent_index.isValid():
            return parent_index.internalPointer().childCount()
        return self._root.childCount()

    def columnCount(self, index=None):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index=None, role=None):
        print(f'calling data at treemodel index{index}, role={role}')
        if not index.isValid():
            return None
        node = index.internalPointer()
        print(f'node{node}')
        if role == Qt.DisplayRole:
            return node.data(index.column())
        return None
