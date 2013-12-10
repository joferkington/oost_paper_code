from uncertainties import ufloat
from utilities import min_value, max_value

def main():
    print 'Plate motion rate parallel to section'
    print plate_motion()

    print 'Shortening (including ductile) from bed-length'
    print bed_length_shortening()

    print 'Estimated total shortening accomodated by OOSTS'
    print oost_shortening()

    print 'Shortening accommodated by seaward branch of OOSTS'
    print seaward_shortening()

    print 'Percentage of OOST shortening'
    print total_oost_percentage()

    print 'Landward Percentage'
    print landward_percentage()

    print 'Seaward Percentage'
    print seaward_percentage()

def bed_length_balancing():
    """Summed fault heaves from bed-length balancing."""
    present_length = 32

    # 2km error from range in restored pin lines + 10% interpretation error
    restored_length = ufloat(82, 10)

    shortening = restored_length - present_length
    return shortening

def bed_length_shortening():
    """Shortening estimate including volume loss."""
    alpha = ufloat(0.35, 0.1)
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
    avg_age = ufloat(2.3, 0.2) # Ma

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
    section_parallel_rate = ufloat(42.9, 2.1)
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

def total_oost_percentage():
    """
    Percentage of shortening accommdated by out-of-sequence thrusting during
    the development of the present-day outer wedge.

    Returns:
    --------
        percentage : A ufloat with a 2 sigma error representing a unitless 
            ratio (e.g. multiply by 100 to get percentage).
    """
    total_shortening, min_total, max_total = total_convergence()
    return oost_shortening() / total_shortening

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

    duration = ufloat(0.97, 0.07) - ufloat(0.25, 0.25)
    rate = plate_motion()
    total = duration * rate
    return landward_shortening / total

if __name__ == '__main__':
    main()
