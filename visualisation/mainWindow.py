from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
import pyvista as pv
import pyvistaqt as pvqt
import pyqtgraph as pg


class UIWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi('visualisation/mainUI.ui', self)

