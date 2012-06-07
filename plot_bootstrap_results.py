import numpy as np
import matplotlib.pyplot as plt

import utilities
import data
from process_bootstrap_results import get_result

def main():
    fig, ax = plt.subplots()
    ax.set_xlabel('Eastward Slip (m)')
    ax.set_ylabel('Northward Slip (m)')

    offsets = [[0, 0]]
    heaves = [[0,0,0]]

    for hor, name in zip(data.horizons[::-1], data.gulick_names[::-1]):
        results = get_result(hor.name)
        discarded = 200 - results.shape[0]
        print 'Discarded {} points from {}'.format(discarded, hor.name)

        # Plot covariance ellipse...
        dx, dy, slip = plot(ax, results, '# ' + name)
        offsets.append([dx, dy])
        heaves.append(utilities.calculate_heave([dx, dy], hor))


    # Plot plate motion over 200kyr
    utilities.plot_plate_motion(xy=offsets[3], time=2e5)

    # Plot lines connecting the horizons...
    ax.plot(*zip(*offsets), marker='o', color='darkred')

    # Plot heaves...
    heaves = np.array(heaves)
    ax.plot(*heaves[:,:2].T, marker='o', color='green')
    
    # Set aspect ratio of plot to 1 so that azimuths are properly represented
    ax.axis('equal')

    plt.show()

def plot(ax, results, name=None):
    mean = results.mean(axis=0)
    cov = np.cov(results, rowvar=False)
    dx, dy = results.mean(axis=0)

    #ax.plot(*results.T, marker='o', ls='none')

    # Plot an error ellipse around the mean offset
    utilities.plot_error_ellipse(cov, mean, ax=ax, nstd=2, alpha=0.5)

    if name is not None:
        ax.annotate(name, xy=mean)
    return dx, dy, mean

if __name__ == '__main__':
    main()
