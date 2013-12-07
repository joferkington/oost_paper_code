import matplotlib.pyplot as plt

from uncertainties import ufloat
from utilities import plot_uncertain, template

import shortening_calculations as calc

def main():
    fig = plt.figure()
    oost_short, plate_shortening = line_balancing_plot()
    fig.savefig('/data/nankai/OOSTPaper/line_balancing_bar_chart.pdf')

    fig = plt.figure()
    forearc_plot()
    fig.savefig('/data/nankai/OOSTPaper/seaward_bar_char.pdf')

    plt.show()


def line_balancing_plot():
    heaves = calc.bed_length_balancing()
    balancing_shortening = calc.bed_length_shortening()
    plate_shortening, smin, smax = calc.total_convergence()

    yticklabels = []

    plot_uncertain(4, heaves)
    yticklabels.append(template('Bed Length Balancing\n{} km', heaves))

    plot_uncertain(3, balancing_shortening)
    yticklabels.append(
        template('Total Shortening from Balancing\n{} km', balancing_shortening)
        )

    plot_uncertain(2, plate_shortening, hard_min=smin, hard_max=smax)
    yticklabels.append(
        template('Convergence over {} myr\n{} km', [calc.age()[0], plate_shortening])
        )

    oost = calc.oost_shortening()
    plot_uncertain(1, oost)
    yticklabels.append(
        template('Predicted Shortening on OOSTS\n{} km', oost)
        )

    plt.yticks([4, 3, 2, 1], yticklabels)
    plt.draw()
    plt.tight_layout()
    plt.xlabel('Shortening Parallel to Section (km)')

    return oost, plate_shortening

def forearc_plot():
    from process_bootstrap_results import shortening_parallel_to_section
    from process_bootstrap_results import heave_parallel_to_section

    # Shortening from fault kinematics is in meters...
    landward_shortening = shortening_parallel_to_section() / 1000
    min_bound = heave_parallel_to_section() / 1000

    total_oost = calc.oost_shortening()

    yticklabels = []

    plot_uncertain(3, total_oost)
    yticklabels.append(template('Total OOST Shortening\n{} km', total_oost))

    plot_uncertain(2, landward_shortening, hard_min=min_bound)
    yticklabels.append(
        template('Shortening on Landward Branch\nFrom Forearc Uplift {} km', 
                 landward_shortening)
        )

    seaward_shortening = total_oost - landward_shortening

    # Hard minimum from Strasser, et al
    plot_uncertain(1, seaward_shortening, hard_min=1.9)
    yticklabels.append(
        template('Predicted Shortening on \n Seaward Branch {} km', 
                 seaward_shortening)
        )
    xmin, xmax = plt.xlim()
    plt.xlim([0, xmax])

    plt.yticks([3, 2, 1], yticklabels)
    plt.tight_layout()
    plt.xlabel('Shortening Parallel to Section (km)')

if __name__ == '__main__':
    main()
