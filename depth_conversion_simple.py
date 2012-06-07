import os
from osgeo import gdal, osr
import numpy as np
import geoprobe
import matplotlib.pyplot as plt
gdal.UseExceptions()
osr.UseExceptions()

def main():
    basedir, ignored = os.path.split(__file__)
    basedir = os.path.realpath(basedir + 'data/swFaults/')

    timefault = basedir + '/jdk_oos_splay_large_area.swf'
    depthfault = basedir + '/jdk_oos_splay_3d_depth.swf'
    timefault = basedir + '/jdk_big_decollement.swf'
    depthfault = basedir + '/jdk_top_underthrust_3d_depth.swf'

    model, time, depth = rock_velocity(timefault, depthfault)
    timefault2depth(timefault, model)

    plt.figure()
    x = np.linspace(time.min(), time.max()+ 0.5, 20)
    plt.plot(time, depth, 'ro')
    plt.xlabel('One-way travel time (sec)')
    plt.ylabel('Depth (meters)')

    plt.plot(x, np.polyval(model, x))
    plt.show()


class GdalGrid(object):
    """Mimics a geoprobe.horizon or swfault."""
    def __init__(self, filename):
        self.ds = gdal.Open(filename)
        self.band = self.ds.GetRasterBand(1)
        trans = self.ds.GetGeoTransform()
        self.xmin, self.ymin = trans[0], trans[3]

    def __getitem__(self, value):
        x, y = value
        t = gdal.Transformer(self.ds, None, [])
        _, (xi, yi, _) = t.TransformPoint(1, x, y, 0)
        z = self.band.ReadAsArray(int(xi), int(yi), 1, 1)
        return z[0,0]
        
    @property
    def grid(self):
        try:
            return self._grid
        except AttributeError:
            self._grid = self.band.ReadAsArray()
            return self._grid

class GridInModelCoords(GdalGrid):
    proj_number = 32653 # UTM Zone 53N, WGS84
    default_volume = '/data/nankai/data/Volumes/kumdep01_flipY.3dv.vol'

    def __init__(self, *args, **kwargs):
        volname = kwargs.pop('volname', self.default_volume)
        GdalGrid.__init__(self, *args, **kwargs)
        self.vol = geoprobe.volume(volname)
        self.inproj = osr.SpatialReference()
        self.inproj.ImportFromEPSG(self.proj_number)
        self.outproj = osr.SpatialReference(self.ds.GetProjection())
    def __getitem__(self, value):
        x, y = self.vol.model2world(*value)
        return GdalGrid.__getitem__(self, self._transform_point(x, y))

    def _transform_point(self, x, y):
        trans = osr.CoordinateTransformation(self.inproj, self.outproj)
        x, y, _ = trans.TransformPoint(x, y)
        return x, y

def compare(xyz1, xyz2):
    """Resample xyz1 at the points in xyz2. Returns the resampled z-value in
    xyz1 and the original z-values in xyz2."""
    from scipy.interpolate import LinearNDInterpolator
    interp = LinearNDInterpolator(xyz1[:,:2], xyz1[:,-1])
    result = interp(xyz2[:,:2])
    return result, xyz2[:,-1]


def rock_velocity(timefaultname, depthfaultname):
    """Builds a 1D depth model for sub-seafloor velocities based on two 
    versions of the same fault (one in time and one in depth)."""
    timefault = geoprobe.swfault(timefaultname)
    depthfault = geoprobe.swfault(depthfaultname)

    # Convert to one-way-time in seconds so that the model units apply...
    time = twt2owt(timefault.z)

    # The time project has X defined as crossline instead of inline
    timexyz = np.vstack([timefault.y, timefault.x, time]).T
    depthxyz = depthfault.xyz

    # Sample the seafloor depths, convert them to one-way-time, and subtract
    seadepth = sample_seafloor(timexyz[:,0], timexyz[:,1])
    timexyz[:,-1] -= np.abs(seadepth) / 1500.00

    depthxyz[:,-1] -= np.abs(sample_seafloor(depthfault.x, depthfault.y))

    time, depth = compare(timexyz, depthxyz)
    mask = np.isfinite(time) & np.isfinite(depth)
    time, depth = time[mask], depth[mask]

    model = np.polyfit(time, depth, 2)

    return model, time, depth

def sample_seafloor(X, Y):
    grid = GridInModelCoords('/data/nankai/data/nankai_bathy.tif') 
    return [grid[x, y] for x, y in zip(X, Y)]

def twt2owt(time):
    return time / 2.0 / 1000.

def timefault2depth(faultname, model):
    timefault = geoprobe.swfault(faultname)

    # Convert to one-way-time in seconds so that the model units apply...
    time = twt2owt(timefault.z)

    # The time project has X defined as crossline instead of inline
    x, y, z = timefault.y, timefault.x, time
    seafloor = sample_seafloor(x, y)

    # Sample the seafloor depths, convert them to one-way-time, and subtract
    time = z - np.abs(seafloor) / 1500.00

    # Now convert things to depth..
    depth = np.polyval(model, time)

    # and add back on the seafloor depths...
    depth += np.abs(seafloor)

    # Now make a new swfault...
    xyz = np.vstack([x,y,depth]).T
    idx = timefault._indices
    depthfault = geoprobe.swfault([xyz[item] for item in idx])

    # and write it to disk
    output_name, ext = os.path.splitext(faultname)
    depthfault.write(output_name + '_depth' + ext)
    return timefault

if __name__ == '__main__':
    main()
