import numpy as np
import geoprobe

from fault_kinematics.homogeneous_simple_shear import invert_slip
import data

from interactive_inclined_shear import FaultModel


def forced_direction_inversion(fault, xyz, alpha, azimuth, **kwargs):
    azimuth = np.radians(90 - azimuth)
    dx, dy = np.cos(azimuth), np.sin(azimuth)
    direc = [[dx, dy], [dx, dy]]
    return invert_slip(fault, xyz, alpha, direc=direc, **kwargs)

def visualize(slip, faultxyz, horxyz):
    fault = geoprobe.swfault('/data/nankai/data/swFaults/jdk_oos_splay_large_area_depth.swf')

    azimuth = np.degrees(np.arctan2(*slip[::-1]))
    azimuth = 90 - azimuth
    mag = np.linalg.norm(slip) / 1000

    f = FaultModel(fault, horxyz, origxyz=horxyz, ve=3, azimuth=azimuth, 
                   slip=mag, alpha=data.alpha, calc_fault=faultxyz)
    f.configure_traits()

fault = data.world_xyz(data.fault)
for i, hor in enumerate(data.horizons[::-1]):
    print hor.name
    xyz = data.to_world(data.to_xyz(hor))[::50]

    slip, metric = invert_slip(fault, xyz, alpha=data.alpha, guess=(0,0), 
                               overlap_thresh=1, return_metric=True)
#    slip, metric = forced_direction_inversion(fault, xyz, data.alpha, data.fault_strike+90,
#                                              guess=guess, return_metric=True)

    visualize(slip, fault, xyz)

