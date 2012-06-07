import numpy as np
import multiprocessing
import itertools
import h5py

from fault_kinematics import homogeneous_simple_shear

import sharedmem as shm

import data


class FakePool(object):
    """Mimics multiprocessing.Pool for debugging."""
    def map(self, func, args, chunksize):
        return map(func, args)
    def imap(self, func, args, chunksize):
        return itertools.imap(func, args)


def main():
    fault = data.to_world(data.to_xyz(data.fault))
    fault = shared_array(fault)

    # Initalize output file...
    output = h5py.File('bootstrap.hdf5', 'w')
    group = output.create_group('IndependentBootstrap')
    group.attrs['alpha'] = data.alpha

    pool = multiprocessing.Pool()

    for hor in data.horizons:
        print hor.name

        horxyz = data.to_world(data.to_xyz(hor))
        # Use a shared array...
        horxyz = shared_array(horxyz)

        # Run in parallel...
        slip, var = parallel_bootstrap_slip(fault, horxyz, data.alpha, 
                                pool=pool, numruns=200, numsamples=10000)
        # Save results...
        hor_group = group.create_group(hor.name)
        hor_group.create_dataset('slip', data=slip)
        hor_group.create_dataset('variance', data=var)

    output.close()

def shared_array(arr):
    shared = shm.empty(arr.shape, arr.dtype)
    shared[:] = arr
    return shared

def _invert_inclined_shear(args):
    """Dummy function to work around multiprocessing.pool only accepting
    one iterable argument and needing functions to be visible from __main__."""
    args = list(args)
    numsamples = args[-1]
    args = args[:-1]

    # "Nudge" solution down-dip (give it a starting direction of downdip)
    dipdir = np.radians(data.fault_strike + 90)
    dx, dy = np.cos(dipdir), np.sin(dipdir)
    direc = np.array([[dx,0],[0,dy]], dtype=np.float)

    # Randomly resample fault with replacement
    args[0] = subsample(args[0])

    # Randomly resample horizon (potentially not with replacement, depending 
    # on numsamples) (Horizon is over-sampled anwyay. It's okay to subsample)
    args[1] = subsample(args[1], numsamples)

    kwargs = dict(direc=direc, return_metric=True, overlap_thresh=1)
    (dx,dy), var = homogeneous_simple_shear.invert_slip(*args, **kwargs)

    return dx, dy, var

def subsample(xyz, numsamples=None):
    if numsamples is None:
        numsamples = xyz.shape[0]
    numpoints = xyz.shape[0]
    idx = np.random.randint(0, numpoints, numsamples)
    return xyz[idx]

def parallel_bootstrap_slip(faultxyz, horxyz, alpha, numruns=10000, 
                            numsamples=None, pool=None):
    if pool is None:
        pool = multiprocessing.Pool()

    # Work around pool.map only taking a single argument...
    horizons = itertools.repeat(horxyz, numruns)
    faults = itertools.repeat(faultxyz, numruns)
    alphas = itertools.repeat(alpha, numruns)
    numsamples = itertools.repeat(numsamples, numruns)
    args = itertools.izip(faults, horizons, alphas, numsamples)

    results = pool.map(_invert_inclined_shear, args, chunksize=1)
    data = np.array(results, dtype=np.float)
    slip = data[:,:2]
    var = data[:,2]
    return slip, var

if __name__ == '__main__':
    main()
