import numpy as np
from numpy import cos, sin, arctan, tan, exp, abs, sqrt
from scipy.ndimage import rotate, gaussian_filter


class Projector:
    
    def __init__(self, activity_map, attenuation_map=None, voxel_size=None):
        self.activity_map = activity_map
        self.attenuation_map = np.zeros_like(activity_map) if attenuation_map is None else attenuation_map
        self.voxel_size = np.array([1., 1., 1.]) if voxel_size is None else np.array(voxel_size)
        self.rotation_axis: int = 0
        self.projection_axis: int = 1
        self.rotation_radius: float = (activity_map.shape[self.projection_axis]*self.voxel_size[self.projection_axis])/2
        self.angles: list = []
        self.set_spatial_resolution(7.4)
        self.noise: bool = True
        self.mean_counts: int = 100_000
        self._axes_planes = np.array([(1, 2), (0, 2), (0, 1)])
        self.blurring_method: str = 'sum'
        self.rng = np.random.default_rng()
    
    @property
    def sum_counts(self):
        return self.mean_counts*len(self.angles)
    
    @sum_counts.setter
    def sum_counts(self, value):
        self.mean_counts = value/len(self.angles)
    
    @property
    def half_tan_fi(self):
        return tan(self.fi)/2
    
    @half_tan_fi.setter
    def half_tan_fi(self, value):
        self.fi = arctan(2*value)
    
    @property
    def distance_to_phantom(self):
        axis = self.projection_axis
        return self.rotation_radius - self.activity_map.shape[axis]*self.voxel_size[axis]/2
    
    def set_spatial_resolution(self, value, distance=100):
        self.half_tan_fi = distance/value
        
    def get_rotated_voxel_size(self, angle):
        angle = np.radians(angle)
        rotation_plane = self._axes_planes[self.rotation_axis]
        rotated_voxel_size = self.voxel_size.copy()
        rot = np.array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
        diff_vector = self.voxel_size[rotation_plane] - self.voxel_size[rotation_plane].min()
        rotated_voxel_size[rotation_plane] -= diff_vector
        rotated_voxel_size[rotation_plane] += np.dot(rot, diff_vector)
        return abs(rotated_voxel_size)
    
    def get_rotated_activity_map(self, angle):
        rotation_plane = self._axes_planes[self.rotation_axis]
        return rotate(self.activity_map, angle, axes=rotation_plane, reshape=False, order=1)
    
    def get_rotated_attenuation_map(self, angle):
        rotation_plane = self._axes_planes[self.rotation_axis]
        return rotate(self.attenuation_map, angle, axes=rotation_plane, reshape=False, order=1)
    
    def get_step_distance(self, angle):
        voxel_size = self.get_rotated_voxel_size(angle)
        return voxel_size[self.projection_axis]
    
    def get_sigma_vector(self, angle):
        projection_plane = self._axes_planes[self.projection_axis]
        voxel_size = self.get_rotated_voxel_size(angle)
        return voxel_size[projection_plane]
    
    def get_sigma_at_distance(self, distance):
        FWHM = distance/self.half_tan_fi
        return FWHM/2.36
    
    def get_detector_slice(self, angle):
        axis = self.projection_axis
        step_distance = self.get_step_distance(angle)
        size = self.attenuation_map.shape[axis]
        detector_slice = int(self.rotation_radius/step_distance + size/2)
        return size if detector_slice >= size else detector_slice + 1
        
    def culculate_escape_probability(self, angle):
        attenuation_map = self.get_rotated_attenuation_map(angle)
        step_distance = self.get_step_distance(angle)
        escape_probability = np.zeros_like(attenuation_map)
        
        axis = self.projection_axis
        detector_slice = self.get_detector_slice(angle)
        
        indices = [slice(None)]*3
        indices[axis] = slice(detector_slice)
        
        if self.blurring_method == 'sum':
            for i in range(detector_slice):
                indices[axis] = slice(i, detector_slice)
                sum_attenuation = attenuation_map[tuple(indices)].sum(axis=axis)
                indices[axis] = i
                escape_probability[tuple(indices)] = exp(-sum_attenuation*step_distance)
        elif self.blurring_method == 'step':
            escape_probability[tuple(indices)] = exp(-attenuation_map[tuple(indices)]*step_distance)
        else:
            raise ValueError(self.blurring_method)
        return escape_probability
    
    def get_projection(self, angle=0.):
        activity_map = self.get_rotated_activity_map(angle)
        escape_probability = self.culculate_escape_probability(angle)
        
        sigma_vector = self.get_sigma_vector(angle)
        step_distance = self.get_step_distance(angle)
        
        axis = self.projection_axis
        detector_slice = self.get_detector_slice(angle)
        indices = [slice(None)]*3
        indices[axis] = slice(detector_slice)
        
        if self.blurring_method == 'sum':
            activity_map = activity_map*escape_probability
            for i in range(detector_slice):
                indices[axis] = i
                distance = step_distance*(detector_slice - i) + self.distance_to_phantom
                sigma = self.get_sigma_at_distance(distance)
                activity_map[tuple(indices)] = gaussian_filter(activity_map[tuple(indices)], sigma/sigma_vector)
            projection = activity_map.sum(self.projection_axis)
            
        elif self.blurring_method == 'step':
            projection_plane = self._axes_planes[axis]
            projection = np.zeros(np.array(activity_map.shape)[projection_plane])
            for i in range(detector_slice):
                indices[axis] = i
                activity_slice = activity_map[tuple(indices)]
                current_sigma = 0.
                for j in range(i, detector_slice):
                    indices[axis] = j
                    step = j - i + 1
                    distance = step_distance*step
                    acuired_sigma = self.get_sigma_at_distance(distance)
                    sigma = sqrt((acuired_sigma**2 - current_sigma**2))
                    activity_slice = gaussian_filter(activity_slice, sigma/sigma_vector)*escape_probability[tuple(indices)]
                    current_sigma = acuired_sigma
                if self.distance_to_phantom > 0:
                    acuired_sigma = self.get_sigma_at_distance(self.distance_to_phantom + distance)
                    sigma = sqrt((acuired_sigma**2 - current_sigma**2))
                    activity_slice = gaussian_filter(activity_slice, sigma/sigma_vector)*escape_probability[tuple(indices)]
                projection += activity_slice
        else:
            raise ValueError(self.blurring_method)
        return projection
    
    def add_poisson_noise(self, projections):
        projections *= self.sum_counts/projections.sum()
        projections[...] = self.rng.poisson(projections)
        
    def start(self):
        projections = []
        for angle in self.angles:
            print(f'Angle: {angle}')
            projection = self.get_projection(angle)
            projections.append(projection)
        projections = np.array(projections)
        if self.noise:
            self.add_poisson_noise(projections)
            projections = projections.astype(int)
        return projections
