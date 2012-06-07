import matplotlib.pyplot as plt
import section
import data

horizons = data.horizon_names

wells = ['C0001A', 'C0002A', 'C0004A', 'C0008A', 'C0009A']

manager = section.NankaiSections(horizons=horizons, wells=wells, ve=3,
            colormap='/data/nankai/data/Colormaps/brown_black',
            well_threshold=200)

fig, axes = plt.subplots(nrows=2, figsize=(16, 13))

for ax, style in zip(axes, [None, 'sketch']):
    sec = manager.add_inline(2695, ymin=5000, ymax=8000, zmin=1500, zmax=4000, 
                            plot_wells=False, ax=ax, style=style)
    manager.wells.plot_on_section(sec, ticks=False)
    sec.ax.invert_xaxis()
    sec.seafloor_mute('/data/nankai/data/Horizons/jdk_seafloor.hzn', pad=15)
    sec.plot_scalebar(length=5000, title='5 km')
    sec.dip_rose(values=range(0, 25, 5))

fig.savefig('/data/nankai/OOSTPaper/forearc_detail_xsec.pdf', dpi=300)


fig, axes = plt.subplots(nrows=2, figsize=(16, 13))

for ax, style in zip(axes, [None, 'sketch']):
    sec = manager.add_crossline(6700, zmin=1500, zmax=3500, 
                            plot_wells=False, ax=ax, style=style)
    manager.wells.plot_on_section(sec, ticks=False)
    sec.seafloor_mute('/data/nankai/data/Horizons/jdk_seafloor.hzn', pad=15)
    sec.plot_scalebar(length=2000, title='2 km')
    sec.dip_rose(values=range(0, 25, 5))

fig.savefig('/data/nankai/OOSTPaper/forearc_detail_strikesec.pdf', dpi=300)


manager.show()
            
