"""
Restores the uplifted horizons while restricting slip along the fault to the
specified azimuth.
"""
import numpy as np
import matplotlib.pyplot as plt

from fault_kinematics.homogeneous_simple_shear import invert_slip
import data
import basic

def main():
    azimuth = data.fault_strike + 90
#    azimuth = 304 # Plate motion from Loveless & Meade
    def func(*args, **kwargs):
        return forced_direction_inversion(azimuth, *args, **kwargs)
    slips, heaves, variances, planar_variances = basic.restore_horizons(func)
    basic.plot_restored_locations(slips, heaves)
    plt.show()

def forced_direction_inversion(azimuth, fault, xyz, alpha, **kwargs):
    """Forces the inversion to only consider slip along the given azimuth."""
    azimuth = np.radians(90 - azimuth)
    dx, dy = np.cos(azimuth), np.sin(azimuth)
    direc = [[dx, dy], [dx, dy]]
    return invert_slip(fault, xyz, alpha, direc=direc, **kwargs)


if __name__ == '__main__':
    main()
