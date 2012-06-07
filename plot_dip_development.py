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
plt.bar(x, dips, align='center', label='Present-day dip')

difs = -np.diff(dips)
plt.plot(x[1:] - 0.5, difs, 'ro-', label='Change in dip')

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
    theta = np.radians(strike)
    ax.plot([theta, theta], [0, 1], 'r-')
ax.set_yticklabels([])
print strikes
print np.mean(strikes)

plt.show()
