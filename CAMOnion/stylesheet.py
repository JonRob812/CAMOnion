from PyQt5.QtCore import QFile, QTextStream
import CAMOnion.resources.breeze_resources


class Style:
    def __init__(self, file):
        self.file = QFile(file)
        self.file.open(QFile.ReadOnly | QFile.Text)
        self.style = QTextStream(self.file).readAll()
        self.string = file[2:-4]

    def __str__(self):
        return self.string


dark = Style(":/dark.qss")
light = Style(":/light.qss")
