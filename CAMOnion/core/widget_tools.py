def get_combo_data(combo_widget):
    return combo_widget.itemData(combo_widget.currentIndex())


def get_combo_data_index(combo_widget, index):
    return combo_widget.itemData(index)


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def get_depths_from_layout(layout):
    depths = {}
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        depths[widget.label_text] = widget.depth_input.text()
    return depths
