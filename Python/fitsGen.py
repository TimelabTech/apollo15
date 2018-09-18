#!/usr/bin/python
# -*- coding: utf-8 -*-

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
lc = lcHelper.filter_by_gti(lc, consts.GTIS)

att = attHelper.load_attitude(consts.ATT_FILE)

height = int(180.0 * consts.IMG_SCALE)
width = int(360.0 * consts.IMG_SCALE)
img_data = np.zeros((height, width))
img_avg_data = np.zeros((180, 360))
img_avg_counts_data = np.zeros((180, 360))

# Calculates the avg energy per ra dec and max energy
max_energy = 0
for i in range(0, len(lc[:, 0])):

    coords = attHelper.get_ra_dec(lc[i, 0], att)

    ra_int = int(coords[0])
    dec_int = int(coords[1] + 90.0)

    total_energy = lcHelper.get_sum_of_energies(lc[i,:])

    if total_energy > 0:
        img_avg_counts_data[dec_int, ra_int] += 1
        img_avg_data[dec_int, ra_int] += (total_energy - img_avg_data[dec_int, ra_int]) / img_avg_counts_data[dec_int, ra_int]
        max_energy = max(img_avg_data[dec_int, ra_int], max_energy)


# For each ra dec use the avg to generate the final img
for dec in range(0, 180):
    for ra in range(0, 360):
        if img_avg_data[dec, ra] > 0:
            ra_int = int(ra * consts.IMG_SCALE)
            dec_int = int(dec * consts.IMG_SCALE)
            color = (img_avg_data[dec, ra] / max_energy) * 255
            img_data = imgHelper.drawFOV(ra_int, dec_int, color, img_data, 255) # img_avg_data[dec, ra]**0.2


# Plot the pointing image
plt.imshow(img_avg_data)
plt.show()

# Plot the image
plt.imshow(img_data)

# Draws SCO X-1
plt.annotate('SCO X-1', xy=(244.979 * consts.IMG_SCALE, (-15.640 + 90) * consts.IMG_SCALE),
             xycoords='data', xytext=(0.5, 0.5), textcoords='figure fraction',
             arrowprops=dict(arrowstyle="->"))

plt.colorbar()
plt.show()


#Plot the histogram
NBINS = 100
histogram = plt.hist(img_data.flatten(), NBINS)
plt.show()


#Img equalization
new_img = hist.histeq(img_data)
plt.imshow(new_img)
plt.show()

#Plot the eq histogram
NBINS = 100
histogram = plt.hist(new_img.flatten(), NBINS)
plt.show()
