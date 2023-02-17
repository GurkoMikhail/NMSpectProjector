import numpy as np
from SimpleITK import ReadImage, GetArrayFromImage, GetImageFromArray, WriteImage
from projector import Projector

def siringe_test():
    activity_map = np.zeros((101, 300, 101), dtype=float)
    activity_map[50, 0, 50] = 1
    projector = Projector(activity_map)
    projector.noise = False
    projector.blurring_method = 'sum'
    projections = []
    for distance in np.linspace(50, 300, 5):
        projector.rotation_radius = distance
        projection = projector.get_projection()
        projections.append(projection)
    projections = np.array(projections)
    projections = GetImageFromArray(projections)
    WriteImage(projections, f'output/siringe_test_{projector.blurring_method}.mha')
        
    
def lung_test():
    activity_map_image = ReadImage('input/activity_map.mhd')
    # attenuation_map_image = ReadImage('input/attenuation_map.mhd')
    activity_map = GetArrayFromImage(activity_map_image)
    # attenuation_map = GetArrayFromImage(attenuation_map_image)
    print(np.unique(activity_map))
    attenuation_map = np.ones_like(activity_map, dtype=float)*0.0162
    attenuation_map[activity_map == 0.] = 0.
    attenuation_map[activity_map == 10.] = 0.0035
    attenuation_map[activity_map == 20.] = 0.0298
    attenuation_map[activity_map == 40.] = 0.0146
    print(np.unique(attenuation_map))
    
    voxel_size = np.array(activity_map_image.GetSpacing())
    
    projector = Projector(activity_map, attenuation_map, voxel_size)
    projector.blurring_method = 'step'
    projector.noise = False
    # projector.rotation_radius = 50.
    projector.angles = np.linspace(0, 360, 30, endpoint=False)
    projections = projector.start()
    projections = np.rot90(projections, k=2, axes=(1, 2))
    projections = GetImageFromArray(projections)
    WriteImage(projections, f'output/projections_{projector.blurring_method}.mha')

if __name__ == '__main__':
    siringe_test()
    # lung_test()