import numpy as np
import matplotlib.pyplot as plt

import geoprobe

from fault_kinematics.homogeneous_simple_shear import _Shear, invert_slip
import data


def planar_variance(xyz):
    vecs, vals = geoprobe.utilities.principal_axes(*xyz.T, return_eigvals=True)
    return vals[-1]

hor = data.horizons[0]
fault = data.to_world(data.to_xyz(data.fault))
xyz = data.to_xyz(hor)[::100]
xyz = data.to_world(xyz)

alpha = data.alpha

func = _Shear(fault, xyz, alpha=alpha, overlap_thresh=0.1)

planar_var = planar_variance(xyz)
slip, thresh = invert_slip(fault, xyz, alpha=alpha, return_metric=True)
print planar_var, thresh


dx, dy = slip
width = 2000
height = 2000
xx, yy = np.mgrid[dx-width:dx+width:100, dy-height:dy+height:100]
roughness = np.zeros(xx.shape, dtype=np.float)

for i, j in np.ndindex(xx.shape):
    roughness[i,j] = func((xx[i,j],yy[i,j]))
roughness = np.ma.masked_greater(roughness, 1.1 * thresh)

flat_point = np.unravel_index(roughness.argmin(), roughness.shape)
plt.pcolormesh(xx, yy, roughness)
plt.plot(dx, dy, 'ro')
plt.colorbar()
plt.axis('tight')
plt.axis('equal')
plt.show()



