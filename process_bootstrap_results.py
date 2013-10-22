import h5py
import numpy as np
import matplotlib.pyplot as plt
import utilities
import data

from uncertainties import ufloat

def main():
    print 'Total Shortening (km)'
    print shortening_magnitude() / 1000.0

    print 'Total Shortening parallel to section (km)'
    print shortening_parallel_to_section() / 1000.0

    print 'Total Shortening perpendicular to section (km)'
    print shortening_perp_to_section() / 1000.0

    print 'At an azimuth of (deg)'
    print shortening_azimuth()

    print 'Total heave (km)'
    print np.linalg.norm(heave()) / 1000.0

    print 'Heave parallel to section... (km)'
    print heave_parallel_to_section()/ 1000.0

    print 'Heave perpendicular to section... (km)'
    print heave_perp_to_section() / 1000.0

def bootstrap_results():
    f, group = load()

    # Use all the trial runs from horizons 7 & 8 to get an average shortening
    # and estimate error.
    names = ['jdk_forearc_horizon_7', 'jdk_forearc_horizon_6', 
             'jdk_forearc_horizon_5', 'jdk_forearc_horizon_4']

    results = np.vstack([get_result(name, group) for name in names])

    f.close()
    return results

def get_result(name, group=None):
    """Get the subset of the bootstrap results where the inversion converged."""
    if group is None:
        f, dat = load()
    else:
        dat = group

    slips = dat[name]['slip'].value
    var = dat[name]['variance'].value

    # Remove results where the resulting variance is an outlier...
    mask = ~utilities.is_outlier(var)

    if group is None:
        f.close()

    return slips[mask]

def recent_offset():
    results = get_result('jdk_forearc_gulick_3-a')

    mean = results.mean(axis=0)
    cov = np.cov(results, rowvar=False)

    slip_vec = mean / np.linalg.norm(mean)
    azimuth = 90 - np.degrees(np.arctan2(*slip_vec[::-1])) + 360

    return np.linalg.norm(mean), error(slip_vec, cov), azimuth

def load():
    f = h5py.File('bootstrap.hdf5', 'r')
    group = f['IndependentBootstrap']
    return f, group

def total_shortening():
    results = bootstrap_results()

    # Mean and covariance for error...
    mean = results.mean(axis=0)
    cov = np.cov(results, rowvar=False)
    return mean, cov

def heave():
    results = bootstrap_results()
    slip = results.mean(axis=0)

    offset = utilities.calculate_heave(slip, data.horizons[0])
    return offset[:2]

def heave_parallel_to_section():
    full_heave = heave()
    section = section_unit_vector()
    return full_heave.dot(section)

def heave_perp_to_section():
    full_heave = heave()
    direc = _perp_vector(section_unit_vector())
    return full_heave.dot(direc)

def section_unit_vector():
    angle = 90 - np.radians(330)
    return np.array([np.cos(angle), np.sin(angle)])

def _parallel_to_vector(measurement, cov, direction):
    result = direction.dot(measurement)
    two_sigma = error(direction, cov)
    return ufloat(result, two_sigma)

def _perp_vector(direction):
    dx, dy = direction
    return np.cross([dx, dy, 0], [0, 0, 1])[:2]

def shortening_parallel_to_section():
    mean, cov = total_shortening()
    direc = section_unit_vector()
    return _parallel_to_vector(mean, cov, direc)

def shortening_perp_to_section():
    mean, cov = total_shortening()
    direc = _perp_vector(section_unit_vector())
    return _parallel_to_vector(mean, cov, direc)


def shortening_magnitude():
    mean, cov = total_shortening()

    slip_dir = mean / np.linalg.norm(mean)

    shortening = np.linalg.norm(mean)
    two_sigma = error(slip_dir, cov)
    return ufloat(shortening, two_sigma)

def shortening_azimuth():
    mean, cov = total_shortening()

    slip_dir = mean / np.linalg.norm(mean)
    return azimuth(slip_dir)

def azimuth(slip):
    azi = 90 - np.degrees(np.arctan2(*slip[::-1]))
    if azi < 0:
        azi += 360
    return azi

def error(direction, cov):
    std = np.sqrt(np.linalg.norm(direction.dot(cov)))
    return 2 * std

def all_results():
    f, group = load()
    results = [get_result(hor.name, group) for hor in data.horizons]
    f.close()
    return results

def mean_slip_vectors():
    return [item.mean(axis=0) for item in all_results()]

def azimuths():
    return [azimuth(item) for item in mean_slip_vectors()]

if __name__ == '__main__':
    main()
