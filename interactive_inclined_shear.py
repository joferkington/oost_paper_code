from traits.api import HasTraits, Range, Instance, \
        on_trait_change
from traitsui.api import View, Item, Group

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                MlabSceneModel

from shapely.geometry import Polygon
import numpy as np
from scipy.interpolate import LinearNDInterpolator

import geoprobe
from fault_kinematics.homogeneous_simple_shear import inclined_shear

import data


class FaultModel(HasTraits):
    azimuth = Range(-180., 180., data.fault_strike - 90, mode='slider')
    slip = Range(-20., 40., 0., mode='slider')
    alpha = Range(-80., 80., data.alpha, mode='slider')

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)

    def __init__(self, fault, horxyz, origxyz=None, ve=2, calc_fault=None, 
                **kwargs):
        self.ve = ve
        self.origxyz = origxyz

        self.fault = fault
        if calc_fault is None:
            self.faultxyz = data.to_world(data.to_xyz(fault))
        else:
            self.faultxyz = calc_fault
        self.horxyz = horxyz

        HasTraits.__init__(self, **kwargs)


    def setup_plot(self):
        tri = triangles(self.fault)
        fault = self.view_triangles(data.world_xyz(self.fault), tri)
#        fault = self.view_xyz_surface(data.world_xyz(self.fault))
        if self.origxyz is not None:
            self.view_xyz_surface(self.origxyz)
        self.scene.mlab.orientation_axes()
        self.scene.mlab.outline(fault)
        return self.view_xyz_surface(self.horxyz)
    
    @on_trait_change('azimuth,slip,alpha,scene.activated')
    def update_plot(self):
        if self.plot is None:
            self.plot = self.setup_plot()
        azi = np.radians(90 - self.azimuth)
        dx, dy = self.slip * np.cos(azi), self.slip * np.sin(azi)
        dx, dy = 1000 * dx, 1000 * dy
        moved = inclined_shear(self.faultxyz, self.horxyz, (dx, dy), self.alpha,
                               remove_invalid=False)
        x, y, z = moved.T
        z *= self.ve
        self.plot.mlab_source.set(x=x, y=y, z=z, scalars=z)


    def view_triangles(self, xyz, tri):
        x, y, z = xyz.T
        z = z * self.ve
        return self.scene.mlab.triangular_mesh(x, y, z, tri)

    def view_xyz_surface(self, xyz):
        tri = LinearNDInterpolator(xyz[:,:2], xyz[:,-1])
        return self.view_triangles(xyz, tri.tri.vertices)

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=600, width=800, show_label=False),
                Group(
                    '_', 'azimuth', 'slip', 'alpha',
                    ),
                resizable=True,
                )

def triangles(fault):
    if isinstance(fault, basestring):
        fault = geoprobe.swfault(fault)
    # Iterate through triangles in internal coords and select those inside 
    # outline the non-convex outline of the fault...
    xyz = fault._internal_xyz
    rotated_tri = LinearNDInterpolator(xyz[:,:2], xyz[:,-1])
    rotated_xyz = fault._internal_xyz
    rotated_outline = Polygon(fault._rotated_outline)

    def inside_outline(tri):
        return rotated_outline.contains(Polygon(rotated_xyz[tri]))

    triangles = rotated_tri.tri.vertices
    return np.array([tri for tri in triangles if inside_outline(tri)])


if __name__ == '__main__':
    fault = geoprobe.swfault('/data/nankai/data/swFaults/jdk_oos_splay_large_area_depth.swf')
    hor = data.horizons[0]
    horxyz = data.to_world(data.to_xyz(hor))[::100]

    plot = FaultModel(fault, horxyz)
    plot.configure_traits()
