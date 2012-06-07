import numpy as np

import geoprobe
from fault_kinematics.homogeneous_simple_shear import invert_slip

import data
from interactive_inclined_shear import FaultModel


def main():
    fault = geoprobe.swfault('/data/nankai/data/swFaults/jdk_oos_splay_large_area_depth.swf')

    faultxyz = data.to_world(data.to_xyz(data.fault))

    horxyz = data.to_world(data.to_xyz(data.horizons[0]))[::100]

    slip = invert_slip(faultxyz, horxyz, alpha=data.alpha)

    azimuth = np.degrees(np.arctan2(*slip[::-1]))
    azimuth = 90 - azimuth
    mag = np.linalg.norm(slip) / 1000

    f = FaultModel(fault, horxyz, origxyz=horxyz, ve=3, azimuth=azimuth, 
                   slip=mag, alpha=data.alpha, calc_fault=faultxyz)
    f.configure_traits()

main()

