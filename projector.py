import numpy as np
from scipy.ndimage import rotate, gaussian_filter
from SimpleITK import ReadImage, GetArrayFromImage, GetImageFromArray, WriteImage


class Projector:
    
    def __init__(self, activity_map, attenuation_map):
        super().__init__()
        self.activity_map = activity_map
        self.attenuation_map = attenuation_map
        self.angles: list = []
        self.spatial_resolution: float = 4.
        self.noise: bool = True
        self.sum_counts: int = 10_000_000
        self.rng = np.random.default_rng()
        
    def culculate_escape_probability(self, attenuation_map, distance_step=1):
        escape_probability = np.zeros_like(attenuation_map)
        for i in range(attenuation_map.shape[-1]):
            sum_attenuation = attenuation_map[:, i:].sum(axis=1)
            escape_probability[:, i] = np.exp(-sum_attenuation*distance_step)
        return escape_probability
    
    def project(self, activity_map, angle, attenuation_map, voxel_size=1):
        rotated_activity_map = rotate(activity_map, angle, axes=(1, 2), reshape=False, order=1)
        rotated_attenuation_map = rotate(attenuation_map, angle, axes=(1, 2), reshape=False, order=1)
        distance_step = np.linalg.norm(np.asarray([np.cos(voxel_size[1]), np.sin(voxel_size[2])])*voxel_size[1:])
        escape_probability = self.culculate_escape_probability(rotated_attenuation_map, distance_step)
        weighted_activity_map = rotated_activity_map*escape_probability
        self.add_blurring(weighted_activity_map)
        projection = (weighted_activity_map).sum(axis=1)
        return projection
    
    def add_blurring(self, activity_map):
        resolutions = np.linspace(self.spatial_resolution, self.spatial_resolution/2, activity_map.shape[-1], endpoint=True)
        for i, resolution in enumerate(resolutions):
            activity_map[:, i] = gaussian_filter(activity_map[:, i], sigma=resolution/2.36, order=0)
            
    def add_poisson_noise(self, projections):
        projections *= self.sum_counts/projections.sum()
        projections[...] = self.rng.poisson(projections)
        
    def start(self):
        attenuation_map = GetArrayFromImage(self.attenuation_map)
        attenuation_map /= 10
        activity_map = GetArrayFromImage(self.activity_map)
        direction = self.activity_map.GetDirection()
        spacing = np.asarray(self.activity_map.GetSpacing())
        
        projections = []
        for angle in self.angles:
            projection = self.project(activity_map, angle, attenuation_map, spacing)
            projections.append(projection)
        projections = np.rot90(projections, k=2, axes=(1, 2))
        
        if self.noise:
            self.add_poisson_noise(projections)
            projections = projections.astype(int)
        
        projections = GetImageFromArray(projections)
        projections.SetSpacing(spacing)
        projections.SetDirection(direction)
        return projections


if __name__ == '__main__':
    activity_map = ReadImage('input/activity_map.mhd')
    attenuation_map = ReadImage('input/attenuation_map.mhd')
    
    projector = Projector(activity_map, attenuation_map)
    projector.angles = [angle for angle in range(0, 360, 6)]
    projections = projector.start()
    WriteImage(projections, 'output/projections_poisson.mha')
    