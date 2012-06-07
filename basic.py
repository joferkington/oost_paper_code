import numpy as np
import matplotlib.pyplot as plt
import geoprobe

from fault_kinematics.homogeneous_simple_shear import invert_slip
import utilities
import data

def forced_direction_inversion(fault, xyz, alpha, azimuth, **kwargs):
    azimuth = np.radians(90 - azimuth)
    dx, dy = np.cos(azimuth), np.sin(azimuth)
    direc = [[dx, dy], [dx, dy]]
    return invert_slip(fault, xyz, alpha, direc=direc, **kwargs)

def planar_variance(xyz):
    vecs, vals = geoprobe.utilities.principal_axes(*xyz.T, return_eigvals=True)
    return vals[-1]

fault = data.to_world(data.to_xyz(data.fault))

slips = [(0,0)]
guess = (0,0)

heaves = [(0,0,0)]
planar_variances = []
variances = []

for i, hor in enumerate(data.horizons[::-1]):
    print hor.name
    xyz = data.to_xyz(hor)[::50]
    xyz = data.to_world(xyz)

    slip, metric = invert_slip(fault, xyz, alpha=data.alpha, guess=guess, 
                               overlap_thresh=1, return_metric=True)
    heave = utilities.calculate_heave(slip, hor)

    variances.append(metric)
    planar_var = planar_variance(xyz)
    planar_variances.append(planar_var)
    print metric / planar_var

    slips.append(slip)
    heaves.append(heave)


x, y = np.array(slips).T
plt.plot(x, y, 'bo-')

x, y, z = np.array(heaves).T
plt.plot(x, y, 'go-')


utilities.plot_plate_motion(time=2e5, xy=slips[3])

plt.axis('equal')

plt.show()
