import numpy as np
import pyvista as pv


class MainParameters:
    
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
    
    def set_activity_map(self, map):
        self.activity_map = map
        self.openGLWidgetOfActivityMap.add_volume(map, cmap='jet', opacity='linear')
        self.openGLWidgetOfActivityMap.show_grid()
        self.openGLWidgetOfActivityMap.show_axes()
        
    def set_attenuation_map(self, map):
        self.attenuation_map = map
        self.openGLWidgetOfAttenuationMap.add_volume(map, cmap='bone', opacity='linear')
        self.openGLWidgetOfAttenuationMap.show_grid()
        self.openGLWidgetOfAttenuationMap.show_axes()
        
    
