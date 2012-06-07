import geoprobe
import data
import utilities

from fault_kinematics import homogeneous_simple_shear

from process_bootstrap_results import get_result, load

fault = data.to_world(data.to_xyz(data.fault))
alpha = data.alpha

f, group = load()

for hor in data.horizons:
    print hor.name
    xyz = data.to_world(data.to_xyz(hor))

    slip = get_result(hor.name, group)

    restored = homogeneous_simple_shear.inclined_shear(fault, xyz, slip, alpha)

    print 'Resampling...'
    restored = data.to_model(restored)
    restored = utilities.grid_xyz(restored)
    new_hor = geoprobe.horizon(*restored.T)
    new_hor.write('restored_horizons/' + hor.name + '.hzn')

f.close()

