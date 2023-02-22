from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QDialog


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi('visualisation/mainUI.ui', self)


class ChangeValueDialogBase(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('visualisation/dialogOfChangeValue.ui', self)


class ShapeInputDialogBase(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('visualisation/dialogOfInputShape.ui', self)





