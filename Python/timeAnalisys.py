#!/usr/bin/python
# -*- coding: utf-8 -*-

# This code aims to extract some statistics about the time steps
# of the ligthcurve
# Author: Ricardo Vallés Blanco (Timelab Technologies)

import numpy as np
from utils import ligthcurve_helper as lcHelper
from utils import attitude_helper as attHelper
from utils import img_helper as imgHelper
from utils import hist
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import constants as consts


lc = lcHelper.get_ligthcurve(consts.LC_FILE)
print("LC:")
print(lc.shape)
print(lc[0])
print(lc[-1])

# Creates an array with the time deltas as elements
time_deltas = [0]
prev_time = 0
for i in range(0, len(lc[:, 0])):
    if i > 0:
        delta = lc[i, 0] - prev_time
        if delta < 600.0 / 3600.0:
            time_deltas.append(delta)
        else:
            time_deltas.append(0)
    prev_time = lc[i, 0]

time_deltas = np.array(time_deltas) * 3600

print('Min:', np.min(time_deltas))
print('Max:', np.max(time_deltas))
print('Mean:', np.mean(time_deltas))
print('Stdev:', np.std(time_deltas))

#Plot the timeline
plt.plot(lc[:, 0], time_deltas)
plt.show()

#Plot the histogram
NBINS = 100
histogram = plt.hist(time_deltas, NBINS)
plt.show()
