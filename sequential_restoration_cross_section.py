import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate

import geoprobe
from fault_kinematics.homogeneous_simple_shear import inclined_shear

import data
import process_bootstrap_results

class Section(object):
    numpoints = 300
    def __init__(self):
        x, y = self.section_line()
        self.x, self.y = x, y
        diff = np.diff(np.r_[x[0], x]), np.diff(np.r_[y[0], y])
        self.dist = np.cumsum(np.hypot(*diff))

    def section_line(self):
        def resample(item):
            return np.linspace(item[0], item[1], self.numpoints)
        x = [626538.9783601476, 659780.2625511164]
        y = [3700356.4603633783, 3680243.543275068]
        return resample(x), resample(y)

    def xsec(self, xyz):
        interp = interpolate.LinearNDInterpolator(xyz[:,:2], xyz[:,-1])
        return interp(np.vstack([self.x, self.y]).T)

    def plot(self, xyz, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()
        z = self.xsec(xyz)
        return ax.plot(self.dist/1000, z/1000, **kwargs)
        ax.set_aspect(2)

def plot_horizons(ax, horizons, slip=(0,0)):
    fault = data.world_xyz(data.fault)
    sec = Section()

    ax.set_ylim([-8, -1.5])
    for hor in horizons:
        xyz = data.world_xyz(hor)[::100]
        xyz = inclined_shear(fault, xyz, slip, data.alpha)
        sec.plot(xyz, ax)

    sec.plot(fault, ax, color='red')
    plt.setp(ax.get_xticklabels(), visible=False)

def plot_present_day(fig):
    topax = fig.add_subplot(6,1,1, aspect=2, adjustable='box')
    seafloor = geoprobe.horizon('/data/nankai/data/Horizons/jdk_seafloor.hzn')
    plot_horizons(topax, data.horizons + [seafloor])
    plt.setp(topax.get_xticklabels(), visible=True)
    topax.set_ylabel('Depth (km bsl)')
    topax.set_xlabel('Distance Along Section (km)')
    return topax


def main():
    # Use the mean slip vector from the bootstrapping results...
    slip_vecs = process_bootstrap_results.mean_slip_vectors()

    # Walk through things in reverse order, restoring things to lower slips
    # then to progressively higher slips.
    horizons, slip_vecs = data.horizons[::-1], slip_vecs[::-1]

    fig, axes = plt.subplots(nrows=6, ncols=2, figsize=(12,12),
                        subplot_kw=dict(aspect=2, adjustable='datalim'))

    # Hide the top two subplots and add a centered one with all horizons...
    for ax in axes[0]:
        ax.set_visible(False)
    axes = axes[1:]
    topax = plot_present_day(fig)

    # Sequentially restore and plot horizons.
    for i, (hor, slip, ax) in enumerate(zip(horizons, slip_vecs, axes.T.flat)):
        horizons = data.horizons[:(len(data.horizons) - i)]
        plot_horizons(ax, horizons, slip)

    names = ['Present Day'] + ['Horizon {}'.format(x) for x in data.gulick_names[::-1]]
    for name, ax in zip(names, [topax] + list(axes.T.flat)):
        ax.annotate(name, (0,1), xytext=(6, -6), xycoords='axes fraction',
                    textcoords='offset points', va='top', ha='left')
        ax.grid(True)

    fig.subplots_adjust(hspace=0, wspace=0)
    for ax in axes[-1]:
        plt.setp(ax.get_xticklabels(), visible=True)
        ax.set_xlabel('Distance Along Section (km)')

    for ax in axes[:,1]:
        ax.yaxis.tick_right()
        ax.yaxis.label_position = 'right'

    for i, ax in enumerate(axes.T.flat):
        if (i % 2) == 0:
            plt.setp(ax.get_yticklabels(), visible=True)
        else:
            plt.setp(ax.get_yticklabels(), visible=False)

    fig.savefig('sequential_restoration_cross_section.pdf')
    plt.show()

main()
