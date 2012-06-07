import os

import geoprobe
import numpy as np

basedir = os.path.dirname(__file__)
basedir = os.path.join(basedir, 'data')

fault = geoprobe.swfault(basedir + 'swFaults/jdk_oos_splay_large_area_depth-mod.swf')
vol = geoprobe.volume(basedir + 'Volumes/kumdep_1500_meter_agc.hdf')

# These are in stratigraphic order from oldest to youngest
horizon_names = [
    'jdk_forearc_7.hzn',
    'jdk_forearc_6.hzn',
    'jdk_forearc_5.hzn',
    'jdk_forearc_4.hzn',
    'jdk_forearc_3.5.hzn',
    'jdk_forearc_3.hzn',
    'jdk_forearc_2.5.hzn',
    'jdk_forearc_2.hzn',
    'jdk_forearc_1.5.hzn',
    'jdk_forearc_1.hzn',
    ]

horizon_names = [basedir + 'Horizons/' + item for item in horizon_names]
horizons = [geoprobe.horizon(item) for item in horizon_names]

gulick_names = ['7', '6', '5', '4', '3.5', '3', '2.5', '2', '1.5', '1']

# Best fit shear angle for inclined shear
alpha = 70


def to_xyz(hor):
    return np.vstack([hor.x, hor.y, hor.z]).T

def xyz2hor(xyz):
    return geoprobe.horizon(*xyz.T)

def to_world(points):
    points = np.atleast_2d(points)
    if points.shape[1] == 2:
        return np.vstack(vol.model2world(*points.T)).T
    else:
        x, y, z = points.T
        x, y = vol.model2world(x, y)
        return np.vstack([x, y, -z]).T

def to_model(points):
    points = np.atleast_2d(points)
    if points.shape[1] == 2:
        return np.vstack(vol.world2model(*points.T)).T
    else:
        x, y, z = points.T
        x, y = vol.world2model(x, y)
        return np.vstack([x, y, -z]).T

def world_xyz(hor):
    return to_world(to_xyz(hor))

fault_xyz = world_xyz(fault)
fault_strike, fault_dip = geoprobe.utilities.points2strikeDip(*fault_xyz.T)
