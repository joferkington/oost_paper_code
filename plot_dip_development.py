import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import geoprobe
import data



def dip(hor):
    x, y, z = data.world_xyz(hor).T
    strike, dip = geoprobe.utilities.points2strikeDip(x, y, -z)
    return strike, dip

strikedips = [dip(item) for item in data.horizons]
strikes, dips = zip(*strikedips)

plt.figure()
x = np.arange(len(dips))
plt.bar(x, dips, align='center', label='Present-day dip', color='0.3', 
        width=0.6)
#plt.plot(x, dips, 'o-', color='k', label='Present-day dip')
for x0, y0, name in zip(x, dips, data.gulick_names):
    plt.annotate('#{}'.format(name), (x0, y0), xytext=(0, 4), 
            textcoords='offset points', ha='center', size=13)


difs = -np.diff(dips)
plt.plot(x[1:] - 0.5, difs, 'o-', mfc='0.7', color='0.7', lw=2, ms=8,
        label='Change in dip')

plt.xticks(x, data.gulick_names)
plt.xlabel('Horizon')
plt.ylabel('Average Dip')
plt.axis([-1, len(dips), 0, 5])
plt.title('Present-Day Dip of Forearc Stratigraphy')
plt.legend()


fig = plt.figure()
ax = fig.add_subplot(111, projection='polar')
ax.set_theta_direction(-1)
ax.set_theta_offset(np.radians(90))
for strike in strikes:
    theta = np.radians(strike + 90)
    ax.annotate('', (theta, 1.0), xytext=(0,0), 
        arrowprops=dict(arrowstyle='-|>,head_width=0.3,head_length=0.6', 
                        fc='k'))
ax.set_yticklabels([])

plt.show()
