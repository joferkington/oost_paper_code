"""
Basic restoration of the uplifted forearc horizons using inclined shear
along the imaged fault surface.

The results given in the paper use boostrapping to estimate an error, as well.
(See bootstrap_error.py) This script just does a single best-fit inversion.
""" 
import numpy as np
import matplotlib.pyplot as plt
import geoprobe

from fault_kinematics.homogeneous_simple_shear import invert_slip
import utilities
import data

def main():
    slips, heaves, _, _ = restore_horizons()
    plot_restored_locations(slips, heaves)
    plt.show()

def restore_horizons(func=invert_slip):
    """
    Restore each of the uplifted horizons individually. 

    "func" just allows overriding of the specific inversion (e.g. see 
    "invert_slip_fixed_azimuth.py") without code duplication.
    """
    # Note that we start each horizon at zero offset and restore independently
    guess = (0,0)

    variances, planar_variances = [], []
    slips, heaves = [], []
    for hor in data.horizons[::-1]:
        hor_xyz = data.world_xyz(hor)

        # Downsample the horizon for faster runtime 
        # (No need to include millions of points along the horizon's surface)
        hor_xyz = hor_xyz[::50]

        # Invert for the slip along the fault needed to restore the horizon
        # to horizontal.
        slip, metric = func(data.fault_xyz, hor_xyz, alpha=data.alpha, 
                            guess=guess, overlap_thresh=1, return_metric=True)
        heave = utilities.calculate_heave(slip, hor)

        variances.append(metric)
        planar_var = planar_variance(hor_xyz)
        planar_variances.append(planar_var)
        slips.append(slip)
        heaves.append(heave)

        # Note: We're plotting "metric / planar_var" to allow a direct
        # comparison of the quality of the fit between different horizons. 
        print 'Restoring', hor.name
        print '    Roughness (lower is better):', metric / planar_var
    return slips, heaves, variances, planar_variances 

def plot_restored_locations(slips, heaves):
    """Plot the map-view location of each horizon's restored position."""
    # Prepend the present-day location of 0,0 for plotting...
    slips = [(0,0)] + slips
    heaves = [(0,0,0)] + heaves

    slip_x, slip_y = np.array(slips).T

    heave_x, heave_y, heave_z = np.array(heaves).T


    fig, ax = plt.subplots()
    ax.plot(slip_x, slip_y, 'bo-')
    ax.plot(heave_x, heave_y, 'go-')
    utilities.plot_plate_motion(time=2e5, xy=slips[3])

    plt.axis('equal')

    return fig, ax

def planar_variance(xyz):
    """
    Effectively the "roughness" (the metric minimized during inversion) left
    over after a planar fit.
    """ 
    vecs, vals = geoprobe.utilities.principal_axes(*xyz.T, return_eigvals=True)
    return vals[-1]

if __name__ == '__main__':
    main()
