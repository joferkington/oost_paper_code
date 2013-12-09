"""
Creates a plot showing the variation in percentage of OOSTS vs. Outer wedge 
shortening over time, as well as the overall percentage of shortening 
accommodated by the OOSTS.
"""
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import shortening_calculations as calc
from utilities import plot_ufloat

def main():
    # Based on observed uplift
    #landward_start = ufloat(0.97, 9.8) # in Ma
    landward_max_start = 1.04
    landward_min_start = 0.9
    landward_max_end = 0.5 
    landward_min_end = 0

    # From Strasser, et al, 2009
    seaward_start = 1.95
    seaward_end = 1.24

    fig = plt.figure()
    gs = GridSpec(1, 4)
    ax1 = fig.add_subplot(gs[:,0])
    ax2 = fig.add_subplot(gs[:,1:], sharey=ax1)

    #plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.yaxis.tick_right()

    plot_range(ax1, 1.0,  2, calc.total_oost_percentage())
    ax1.axis([1, 2, 0, 1])
    ax1.set(xticks=[], yticks=[0, 0.25, 0.5, 0.75, 1.0],
            yticklabels=['0%', '25%', '50%', '75%', '100%'])
    ax1.grid(True, axis='y')

    plot_range(ax2, seaward_start, seaward_end, calc.seaward_percentage())
    plot_range(ax2, landward_min_start, landward_max_end, calc.landward_percentage())
    plot_range(ax2, landward_max_start, landward_min_start, 
               calc.landward_percentage(), alpha=0.5, error=False)
    plot_range(ax2, landward_max_end, landward_min_end, 
               calc.landward_percentage(), alpha=0.5, error=False)
    ax2.axis([calc.age()[-1], 0, 0, 1])
    ax2.set_xlabel('Age (Ma)')
    ax2.grid(True, axis='y')

    plt.show()

def plot_range(ax, start, end, percent, error=True, **kwargs):
    width = end - start
    per = percent.nominal_value
    ax.bar([start, start], 
           [per, 1 - per],
           [width, width],
           [0, per],
           color=['red', 'green'], **kwargs)
    if error:
        plot_ufloat(percent, start + width/2, ax=ax, axis='y', 
                    color='black', capsize=10)

main()
