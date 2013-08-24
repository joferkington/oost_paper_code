import numpy as np
import matplotlib.pyplot as plt

from fault_kinematics.homogeneous_simple_shear import inclined_shear
from fault_kinematics.homogeneous_simple_shear import invert_slip

import data
import utilities

fault = data.to_xyz(data.fault)
fault = data.to_world(fault)

models = [[0, 0]]

i = 0
for hor in data.horizons[::-1]:
    print hor.name
    # Downsample horizon for faster solution...
    xyz = data.to_xyz(hor)[::50,:]
    xyz = data.to_world(xyz)

    # Move this horizon to the last horizon's best fit offset.
    # Following the path of all previous horizons...
    for model in models:
        dx, dy = model
        xyz = inclined_shear(fault, xyz, (dx,dy), data.alpha)

    model = invert_slip(fault, xyz, data.alpha, guess=(0,0))
    models.append(model)
    i += 1

models = np.array(models)
movement = models[:,:2].cumsum(axis=0)

x, y = movement.T

plt.plot(x, y, marker='o')

utilities.plot_plate_motion(time=3e5)

plt.axis('equal')
plt.show()
