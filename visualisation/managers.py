import numpy as np
import pyvista as pv
import SimpleITK as sitk
import pyqtgraph as pg
from PyQt5.QtWidgets import QFileDialog
from visualisation.dialogs import ShapeInputDialog, ChangeValueDialog

pg.setConfigOptions(imageAxisOrder='row-major')
pv.set_plot_theme('document')
sargs = dict(
    vertical=True,
    interactive=False,
    height=0.9,
    position_x=0.85,
    position_y=0.05,
    title_font_size=20,
    label_font_size=16,
    shadow=True,
    italic=True,
    font_family="arial",
)

_axes_planes = np.array([(1, 2), (0, 2), (0, 1)])


class MainParameters:
    
    def __init__(self):
        self._activity_map = None
        self._attenuation_map = None
        self._projections = None
        
        self._activity_map_actor = None
        self._attenuation_map_actor = None
    
    @property
    def activity_map(self):
        return self._activity_map.copy() if self._activity_map is np.ndarray else self._activity_map
    
    @activity_map.setter
    def activity_map(self, value):
        self._activity_map = value
        if self._activity_map_actor is None:
            self._activity_map_actor = self.openGLWidgetOfActivityMap.add_volume(value, cmap='jet', opacity='linear', scalar_bar_args=sargs)
            self.openGLWidgetOfActivityMap.add_bounding_box()
            self.openGLWidgetOfActivityMap.add_axes(box=True)
        else:
            self.openGLWidgetOfActivityMap.remove_actor(self._activity_map_actor)
            self._activity_map_actor = self.openGLWidgetOfActivityMap.add_volume(value, cmap='jet', opacity='linear', scalar_bar_args=sargs)
            
    @property
    def attenuation_map(self):
        return self._attenuation_map.copy() if self._attenuation_map is np.ndarray else self._attenuation_map
    
    @attenuation_map.setter
    def attenuation_map(self, value):
        self._attenuation_map = value
        if self._attenuation_map_actor is None:
            self._attenuation_map_actor = self.openGLWidgetOfAttenuationMap.add_volume(value, cmap='bone', opacity='linear', scalar_bar_args=sargs)
            self.openGLWidgetOfAttenuationMap.add_bounding_box()
            self.openGLWidgetOfAttenuationMap.add_axes(box=True)
        else:
            self.openGLWidgetOfAttenuationMap.remove_actor(self._attenuation_map_actor)
            self._attenuation_map_actor = self.openGLWidgetOfAttenuationMap.add_volume(value, cmap='bone', opacity='linear', scalar_bar_args=sargs)
    
    @property
    def projections(self):
        return self._projections.copy() if self._projections is np.ndarray else self._projections
    
    @projections.setter
    def projections(self, value):
        self._projections = value
        self.openGLWidgetOfProjections.setImage(np.rot90(value, k=1, axes=(1, 2)))
        
    @property
    def voxel_size(self):
        x = self.doubleSpinBoxOfVoxelSizeX.value()
        y = self.doubleSpinBoxOfVoxelSizeY.value()
        z = self.doubleSpinBoxOfVoxelSizeZ.value()
        return np.asarray([x, y, z])
    
    @voxel_size.setter
    def voxel_size(self, value):
        x, y, z = value
        self.doubleSpinBoxOfVoxelSizeX.setValue(x)
        self.doubleSpinBoxOfVoxelSizeY.setValue(y)
        self.doubleSpinBoxOfVoxelSizeZ.setValue(z)
    
    @property
    def rotation_radius(self):
        return self.doubleSpinBoxOfRotationRadius.value()
    
    @property
    def rotation_axis(self):
        return self.comboBoxOfRotationAxis.currentIndex()
    
    @property
    def projection_axis(self):
        return self.comboBoxOfProjectionAxis.currentIndex()
    
    @property
    def angles(self):
        start = self.doubleSpinBoxOfAnglesStart.value()
        stop = self.doubleSpinBoxOfAnglesStop.value()
        number = self.spinBoxOfAnglesNumber.value()
        return np.linspace(start, stop, number, endpoint=False)
    
    @property
    def spatial_resolution(self):
        resolution = self.doubleSpinBoxOfResolution.value()
        distance = self.doubleSpinBoxOfResolutionDistance.value()
        return resolution, distance
    
    @property
    def mean_counts(self):
        return self.spinBoxOfMeanCounts.value()
    
    @property
    def noise(self):
        return self.comboBoxOfNoise.currentIndex()
    
    @property
    def blurring_method(self):
        return self.comboBoxOfBlurringMethod.currentText()
    
      
class Editor:
    
    def __init__(self):
        self.actionOpenActivityMap.triggered.connect(self.loadActivityMap)
        self.actionOpenAttenuationMap.triggered.connect(self.loadAttenuationMap)
        
        self.actionSaveActivityMap.triggered.connect(self.saveActivityMap)
        self.actionSaveAttenuationMap.triggered.connect(self.saveAttenuationMap)
        self.actionSaveProjections.triggered.connect(self.saveProjections)
        
        self.actionChangeActivityMap.triggered.connect(self.changeActivityMap)
        self.actionChangeAttenuationMap.triggered.connect(self.changeAttenuationMap)
        
        self.loadDirectory = 'input'
        self.saveDirectory = ''
        
    def loadFile(self, fileName):
        _, fileType = fileName.split('.')
        if fileType == 'npy':
            return np.load(fileName)
        if fileType in ('dcm', 'mhd', 'mha'):
            image = sitk.ReadImage(fileName)
            return sitk.GetArrayFromImage(image)
        if fileType == 'dat':
            shape, order = ShapeInputDialog.getShape()
            return np.loadtxt(fileName).reshape(shape, order=order)
        raise ValueError('Неверное расширение файла')
    
    def saveFile(self, fileArray, fileName, **kwargs):
        _, fileType = fileName.split('.')
        if fileType == 'npy':
            np.save(fileName, fileArray)
            return
        if fileType in ('dcm', 'mhd', 'mha'):
            image = sitk.GetImageFromArray(fileArray)
            image.SetSpacing(self.voxel_size)
            sitk.WriteImage(image, fileName)
            return
        if fileType == 'dat':
            np.savetxt(fileName, fileArray)
            return
        raise ValueError('Неверное расширение файла')
    
    def loadActivityMap(self):
        fileName, _ = QFileDialog.getOpenFileName(directory=self.loadDirectory)
        fileArray = self.loadFile(fileName)
        self.activity_map = fileArray
    
    def loadAttenuationMap(self):
        fileName, _ = QFileDialog.getOpenFileName(directory=self.loadDirectory)
        fileArray = self.loadFile(fileName)
        self.attenuation_map = fileArray
        
    def saveActivityMap(self):
        fileName, _ = QFileDialog.getSaveFileName(directory=self.saveDirectory)
        self.saveFile(self.activity_map, fileName)
        
    def saveAttenuationMap(self):
        fileName, _ = QFileDialog.getSaveFileName(directory=self.saveDirectory)
        self.saveFile(self.attenuation_map, fileName)
        
    def saveProjections(self):
        fileName, _ = QFileDialog.getSaveFileName(directory=self.saveDirectory)
        self.saveFile(self.projections, fileName)
        
    def updateProjections(self, value):
        self.projections = value
        self.pushButtonOfRun.setEnabled(True)
        
    def changeActivityMap(self):
        changedActivityMap = ChangeValueDialog.getChangedArray(self.activity_map)
        if changedActivityMap is not None:
            self.activity_map = changedActivityMap
    
    def changeAttenuationMap(self):
        changedAttenuationMap = ChangeValueDialog.getChangedArray(self.attenuation_map)
        if changedAttenuationMap is not None:
            self.attenuation_map = changedAttenuationMap
    
    
    
    