import matplotlib.pyplot as plt
import sys

from fault_kinematics.homogeneous_simple_shear import invert_slip
import data

def optimize_single_alpha():
    """Find the single shear angle that best flattens all horizons using a grid
    search."""
    fault = data.to_world(data.to_xyz(data.fault))
    alphas = range(-80, 85, 5)

    roughness = []
    for alpha in alphas:
        update('Alpha = %i: ' % alpha)

        rough = 0
        for i, hor in enumerate(data.horizons):
            xyz = data.to_world(data.to_xyz(hor))[::50]
            update('%i ' % (len(data.horizons) - i))
            slip, metric = invert(fault, xyz, alpha)
            rough += metric

        update('\n')
        roughness.append(rough)

    fig, ax = plt.subplots()
    ax.plot(alphas, roughness)
    ax.set_title('Optimizing Shear Angle')
    ax.set_ylabel('Summed misfit (m)')
    ax.set_xlabel('Shear angle (degrees)')
    fig.savefig('optimize_single_alpha.pdf')

    plt.show()


def optimize_individual_alpha():
    """Find the best shear angle for each horizon using a grid search."""
    fault = data.to_world(data.to_xyz(data.fault))
    alphas = range(-80, 85, 5)

    for hor in data.horizons:
        update(hor.name + ': ')
        xyz = data.to_world(data.to_xyz(hor))[::50]

        roughness = []
        for i, alpha in enumerate(alphas):
            update('%i ' % (len(alphas) - i)) 
            slip, metric = invert(fault, xyz, alpha)
            roughness.append(metric)

        update('\n')

        fig, ax = plt.subplots()
        ax.plot(alphas, roughness)
        ax.set_title(hor.name)
        ax.set_ylabel('Misfit (m)')
        ax.set_xlabel('Shear angle (degrees)')
        fig.savefig('optimize_alpha_individual_%s.pdf'%hor.name)

    plt.show()

def invert(fault, xyz, alpha):
    return invert_slip(fault, xyz, alpha, overlap_thresh=1, return_metric=True)

def update(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()

optimize_single_alpha()
#optimize_individual_alpha()
