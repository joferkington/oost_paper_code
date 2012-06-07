import numpy as np
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
import geoprobe

from fault_kinematics import homogeneous_simple_shear
import data

def shortening_along_section(mean, cov):
    """Calculates shortening and error projected onto an inline in the 3D 
    seismic volume. Returns shortening parallel to the line and error parallel
    to the line."""
    sec_angle = np.radians(150)
    sec = np.cos(sec_angle), np.sin(sec_angle)
    return mean.dot(sec), np.sqrt(np.linalg.norm(cov.dot(sec)))

def plot_error_ellipse(cov, mean, nstd=2, ax=None, **kwargs):
    """Plots an `nstd` sigma error ellipse based on the specified covariance
    matrix (`cov`) and mean. Additional arguments are passed on to the ellipse
    patch artist."""
    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:,order]

    if ax is None:
        ax = plt.gca()

    vals, vecs = eigsorted(cov)
    theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))

    # Width and height are "full" widths, not radius
    width, height = 2 * nstd * np.sqrt(vals)
    ellip = Ellipse(xy=mean, width=width, height=height, angle=theta, **kwargs)

    ax.add_artist(ellip)
    return ellip

def plot_fault_strike(x0, y0, ax=None, **kwargs):
    xyz = data.to_xyz(data.fault)
    xy = data.to_world(xyz)
    x, y, z = xyz.T
    x, y = xy.T
    strike, dip = geoprobe.utilities.points2strikeDip(x, y, z)
    print strike, dip

def plot_strike_dip(strike, dip, x0, y0, size=18, ax=None, **kwargs):
    """Plots a strike/dip tick at location x0, y0."""
    if ax is None:
        ax = plt.gca()

    tick_ratio = 0.3

    strike = -strike + 90
    if strike < 0:
        strike += 360

    dx = np.cos(np.radians(strike)) * size / 2.0
    dy = np.sin(np.radians(strike)) * size / 2.0
    ddx = tick_ratio * np.cos(np.radians(strike+90)) * size / 2.0
    ddy = tick_ratio * np.sin(np.radians(strike+90)) * size / 2.0

    x1, y1 = [x0-dx, x0+dx], [y0-dy, y0+dy]
    x2, y2 = [x0-ddx, x0], [y0-ddy, y0]

    ax.plot(x1, y1, **kwargs)
    ax.plot(x2, y2, **kwargs)

    ax.annotate('%i' % dip, xy=(x2[0], y2[0]), xytext=(-10, 10), 
                textcoords='offset points')

def plot_plate_motion(ax=None, xy=(0, 0), time=1, ellipkwargs=None, 
                      arrowkwargs=None):
    """
    Plots the plate motion and error ellipse in meters over the specified
    `time` (in years) for the Philippine Sea Plate relative to the Nankai
    Forearc Block using the model from Loveless & Meade, 2010.

    Parameters:
    -----------
        ax : The matplotlib axes object to plot on. (Uses the current axes if
            not specified.)
        xy : A sequence of x, y denoting the starting point for the plate 
            motion arrow.
        time : The duration of time in years that the length of the arrow 
            should represent. 
        ellipkwargs : A dict of additional keyword arguments to pass on to the
            error ellipse.
        arrowkwargs : A dict of additional keyword arguments to pass on to the 
            arrow.

    Returns:
    --------
        arrow : The matplotlib arrow artist representing plate motion
        ellip : The matplotlib ellipse artists representing the error in plate
            motion
    """
    if ax is None:
        ax = plt.gca()
    if ellipkwargs is None:
        ellipkwargs = {}
    if arrowkwargs is None:
        arrowkwargs = {}

    time = time / 1000.0
    x, y = xy

    # Note: This is based on the fault segment nearest the study area rather
    # than an euler pole.
    azimuth = 302.8
    error_width = 2.1
    error_height = 1.4
    rate = 48.0

    theta = np.radians(90 - azimuth)
    dx, dy = np.cos(theta), np.sin(theta)

    dx, dy = dx * rate * time, dy * rate * time
    error_width *= time
    error_height *= time

    ellip = Ellipse(xy=(x + dx, y + dy), width=2*error_width, 
                    height=2*error_height, angle=90-azimuth, **ellipkwargs)
    ax.add_artist(ellip)
    arrow = ax.arrow(x, y, dx, dy, **arrowkwargs)
    return arrow, ellip

def calculate_heave(slip, hor):
    """Calculates the average heave resulting from moving the given horizon
    (`hor`) by `slip` along the main fault."""
    orig_xyz = data.to_world(data.to_xyz(hor))[::50]
    fault = data.to_world(data.to_xyz(data.fault))

    func = homogeneous_simple_shear.inclined_shear
    moved_xyz = func(fault, orig_xyz, slip, data.alpha, remove_invalid=False)

    diff = moved_xyz - orig_xyz
    mask = np.isfinite(diff)
    mask = mask[:,0] & mask[:,1]
    return diff[mask,:].mean(axis=0)

def grid_xyz(xyz):
    """
    Resamples points onto a regular grid with a spacing of 1. This is intended
    for resampling a seismic horizon, thus the dx and dy are fixed at 1.

    Parameters:
    -----------
        xyz : An Nx3 array of points

    Returns:
    --------
        resampled_xyz : An Nx3 array of points "snapped" onto grid locations.
    """
    import scipy.spatial
    tree = scipy.spatial.cKDTree(xyz[:,:2])

    x, y, z = xyz.T
    xmin, xmax = int(x.min()), int(x.max()+1)
    ymin, ymax = int(y.min()), int(y.max()+1)

    xx, yy = np.mgrid[xmin:xmax, ymin:ymax]
    zz = np.empty(xx.shape, dtype=np.float)
    zz.fill(np.nan)

    for i, j in np.ndindex(xx.shape):
        dist, idx = tree.query([xx[i,j], yy[i,j]], k=1, eps=2, 
                            distance_upper_bound=2)
        if np.isfinite(dist):
            zz[i, j] = xyz[idx,2]
    mask = np.isfinite(zz)
    return np.vstack([xx[mask], yy[mask], zz[mask]]).T


def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

