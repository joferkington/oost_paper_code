import matplotlib.pyplot as plt

from uncertainties import ufloat

def main():
    fig = plt.figure()
    oost_short, plate_shortening = line_balancing_plot()
    fig.savefig('/data/nankai/OOSTPaper/line_balancing_bar_chart.pdf')
    print 'Plate motion rate parallel to section'
    print plate_motion()

    print 'Percentage of OOST shortening'
    print oost_short / plate_shortening

    print 'Landward Percentage'
    print landward_percentage()

    print 'Seaward Percentage'
    print seaward_percentage()

    fig = plt.figure()
    forearc_plot()
    fig.savefig('/data/nankai/OOSTPaper/seaward_bar_char.pdf')

    plt.show()


def line_balancing_plot():
    heaves = bed_length_balancing()
    balancing_shortening = bed_length_shortening()
    plate_shortening, smin, smax = total_convergence()

    yticklabels = []

    plot_uncertain(4, heaves)
    yticklabels.append(template('Bed Length Balancing\n{} km', heaves))

    plot_uncertain(3, balancing_shortening)
    yticklabels.append(
        template('Total Shortening from Balancing\n{} km', balancing_shortening)
        )

    plot_uncertain(2, plate_shortening, hard_min=smin, hard_max=smax)
    yticklabels.append(
        template('Convergence over {} myr\n{} km', [age()[0], plate_shortening])
        )

    oost = oost_shortening()
    plot_uncertain(1, oost)
    yticklabels.append(
        template('Predicted Shortening on OOSTS\n{} km', oost)
        )

    plt.yticks([4, 3, 2, 1], yticklabels)
    plt.tight_layout()
    plt.xlabel('Shortening Parallel to Section (km)')

    return oost, plate_shortening

def forearc_plot():
    from process_bootstrap_results import shortening_parallel_to_section
    from process_bootstrap_results import heave_parallel_to_section

    # Shortening from fault kinematics is in meters...
    landward_shortening = shortening_parallel_to_section() / 1000
    min_bound = heave_parallel_to_section() / 1000

    total_oost = oost_shortening()

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


def bed_length_balancing():
    """Summed fault heaves from bed-length balancing."""
    present_length = 32

    # 2km error from range in restored pin lines + 10% interpretation error
    restored_length = ufloat('82+/-10')

    shortening = restored_length - present_length
    return shortening

def bed_length_shortening():
    """Shortening estimate including volume loss."""
    alpha = ufloat('0.5+/-0.1')
    heaves = bed_length_balancing()
    return heaves * (1 + alpha)

def age():
    """
    Age of the oldest in-sequence structures from Strasser, 2009.
    
    Returns:
    --------
        avg_age : A ufloat with an assumed 2 sigma uncertainty
        min_age : The "hard" minimum from Strasser, et al, 2009
        max_age : The "hard" maximum from Strasser, et al, 2009
    """
    min_age = 1.95 # Ma
    max_age = 2.512 # Ma

    # Strasser perfers an older age within this range, so we model this as
    # 2.3 +/- 0.2, but provide mins and maxs
    avg_age = ufloat('2.3+/-0.2') # Ma

    return avg_age, min_age, max_age

def plate_motion():
    """
    Plate motion rate (forearc relative to oceanic plate) _parallel_ _to_
    _section_ (Not full plate vector!) based on elastic block modeling 
    (Loveless&Meade, 2010).

    Returns:
    --------
        rate : A ufloat in mm/yr with a 2 sigma error
    """
    # See /data/MyCode/VariousJunk/loveless_meade_block_model_slip_vector.py
    # for details of derivation... Uses block segment nearest study area instead
    # of derived euler pole.
    # I'm assuming that Loveless's reported errors are 2 sigma...
    section_parallel_rate = ufloat('42.9+/-2.1')
    return section_parallel_rate

def total_convergence():
    """
    Total shortening parallel to section from plate motion and ages.
    
    Returns:
    --------
        shortening : A ufloat representing the plate motion integrated over the 
            age of deformation with a 2 sigma confidence interal.
        min_shortening : A "hard" minimum using the uncertainty in the plate 
            motion and minimum constraints on the age.
        max_shortening : A "hard" maximum using the uncertainty in the plate 
            motion and maximum constraints on the age.
    """
    avg_age, min_age, max_age = age()
    rate = plate_motion()

    shortening = rate * avg_age

    min_shortening = min_value(min_age * rate)
    max_shortening = max_value(max_age * rate)
    return shortening, min_shortening, max_shortening

def oost_shortening():
    """
    Shortening on the out-of-sequence thrust system based on integrated plate
    convergence minus the shortening predicted in the outer wedge from line
    balancing results.

    Returns:
    --------
        shortening : A ufloat with a 2 sigma error estimate
    """
    total_shortening, min_total, max_total = total_convergence()
    return total_shortening - bed_length_shortening()

def seaward_shortening():
    """Shortening accomodated on the seaward branch of the OOSTS based on 
    comparing the total (`oost_shortening()`) shortening with the shortening
    predicted on the landward branch from forearc uplift. 
    
    Returns:
    --------
        shortening : a ufloat with 2 sigma error in kilometers.
    """
    from process_bootstrap_results import shortening_parallel_to_section
    landward_shortening = shortening_parallel_to_section() / 1000
    return oost_shortening() - landward_shortening

def seaward_percentage():
    """
    Percentage of total plate convergence accomodated by the seaward branch of
    the OOSTS during its period of activity.

    Returns:
    --------
        percentage : A ufloat with a 2 sigma error representing a unitless 
            ratio (e.g. multiply by 100 to get percentage).
    """
    # Duration in myr from Strasser, 2009
    duration = 1.95 - 1.24 
    rate = plate_motion()
    total = duration * rate
    return seaward_shortening() / total

def landward_percentage():
    """
    Maximum percentage of total plate convergence accomodated by the landward
    branch of the OOSTS during its period of activity.

    Returns:
    --------
        percentage : A ufloat with a 2 sigma error representing a unitless 
            ratio (e.g. multiply by 100 to get percentage).
    """
    from process_bootstrap_results import shortening_parallel_to_section
    landward_shortening = shortening_parallel_to_section() / 1000

    duration = 1.04 - 0.5 # Probably too short...
    rate = plate_motion()
    total = duration * rate
    return landward_shortening / total


def min_value(uncert_val):
    """Minimum confidence interval for a ufloat quantity."""
    return uncert_val.nominal_value - uncert_val.std_dev()

def max_value(uncert_val):
    """Maximum confidence interval for a ufloat quantity."""
    return uncert_val.nominal_value + uncert_val.std_dev()

def plot_uncertain(y, value, ax=None, hard_min=None, hard_max=None, **kwargs):
    """Plots an bar with errors and optional "hard" minimums and maximums."""
    if ax is None:
        ax = plt.gca()

    ax.barh(y, value.nominal_value, align='center', height=0.6, 
            color='green', **kwargs)
    plot_ufloat(value, y, ax, color='black', capsize=8)

    if hard_min is not None:
        ax.plot(hard_min, y, 'k>')
    if hard_max is not None:
        ax.plot(hard_max, y, 'k<')

def plot_ufloat(value, y, ax=None, **kwargs):
    """Plot errorbars from a ufloat quantity."""
    if ax is None:
        ax = plt.gca()
    return ax.errorbar(value.nominal_value, y, xerr=value.std_dev(), **kwargs)

def template(temp, val):
    """
    Format a ufloat quantity for matplotlib plotting (e.g. nice +/- signs).
    """
    def format_ufloat(val):
        return r'%0.1f$\pm$%0.1f' % (val.nominal_value, val.std_dev())
    if not isinstance(val, list):
        val = [val]
    val = [format_ufloat(item) for item in val]
    return temp.format(*val)

main()
