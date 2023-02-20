import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from visualisation.properties import MainParameters
from visualisation.mainWindow import UIWindow
from projector import Projector
import numpy as np
from vtk_converter import read_dat, read_image, convert_images_to_vtk


class QProjector(Projector, QThread):
    progress = pyqtSignal(int)
    resultReport = pyqtSignal(np.ndarray)
    
    def __init__(self, activity_map, attenuation_map=None, parent=None):
        QThread.__init__(self, parent)
        Projector.__init__(self, activity_map, attenuation_map)
        
    def get_projection(self, angle=0):
        result = super().get_projection(angle)
        index = np.argwhere(self.angles == angle)
        progress = int(100*index/(self.angles.size - 1))
        self.progress.emit(progress)
        return result
    
    def run(self):
        result = super().run()
        self.resultReport.emit(result)


class MainWindow(UIWindow, MainParameters):
    
    def __init__(self):
        super().__init__()
        self.pushButtonOfRun.clicked.connect(self.startProjector)
        
    def updateProjections(self, value):
        mainWindow.openGLWidgetOfProjections.setImage(value)
        self.pushButtonOfRun.setEnabled(True)
    
    def reportProgress(self, value):
        self.progressBar.setValue(value)
    
    def startProjector(self):
        self.pushButtonOfRun.setEnabled(False)
        projector = QProjector(self.activity_map, self.attenuation_map, self)
        projector.voxel_size = self.voxel_size
        projector.rotation_radius = self.rotation_radius
        projector.rotation_axis = self.rotation_axis
        projector.projection_axis = self.projection_axis
        projector.angles = self.angles
        projector.set_spatial_resolution(*self.spatial_resolution)
        projector.mean_counts = self.mean_counts
        projector.noise = self.noise
        projector.blurring_method = self.blurring_method
        projector.progress.connect(self.update)
        projector.progress.connect(self.reportProgress)
        projector.resultReport.connect(self.updateProjections)
        projector.start()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    
    shape = (128, 128, 128)
    
    activity_map = np.loadtxt(f'input/heart_data/heart_32/activity_map.dat').reshape(shape)
    # activity_map *= 256/activity_map.max()
    mainWindow.set_activity_map(activity_map)
    
    attenuation_map = np.loadtxt(f'input/heart_data/attenuation_map.dat').reshape(shape)
    # attenuation_map *= 256/attenuation_map.max()
    attenuation_map /= 10
    mainWindow.set_attenuation_map(attenuation_map)
    
    mainWindow.show()
    app.exec()
    
    