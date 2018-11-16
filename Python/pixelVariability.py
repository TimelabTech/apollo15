#!/usr/bin/python
# -*- coding: utf-8 -*-

# This code is a Sky Pixel Variability data extractor
# Extracts the data of how the energy from a coordinates in the sky varies in time.
# Author: Ricardo Vallés Blanco (ESAC)

import numpy as np
from utils import ligthcurve_helper as lcHelper
from utils import attitude_helper as attHelper
from utils import img_helper as imgHelper
from utils import hist
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import constants as consts


lc = lcHelper.get_ligthcurve(consts.LC_FILE)
lc = lcHelper.filter_by_gti(lc, consts.GTIS)

att = attHelper.load_attitude(consts.ATT_FILE)

n_samples = len(lc[:, consts.LC_TIME_COL])

PIX_SIZE = 10
MAX_RA = 360/PIX_SIZE
MAX_DEC = 180/PIX_SIZE
MIN_ENERGY = 0.02

coords_arr = []
n_obs_per_px_arr = np.zeros((MAX_DEC, MAX_RA))

# Counts the number of perfectly overlaped observations
for i in range(0, n_samples):
    time = lc[i, consts.LC_TIME_COL]
    coords = attHelper.get_ra_dec(time, att)

    ra_int = int(coords[0])/PIX_SIZE
    dec_int = int(coords[1] + 90.0)/PIX_SIZE

    coords_arr.append({ "ra": ra_int, "dec": dec_int })
    n_obs_per_px_arr[dec_int, ra_int] += 1


# Plot the n_obs_per_px_arr
plt.imshow(n_obs_per_px_arr)
plt.colorbar()
plt.show()

max_count = int(np.max(n_obs_per_px_arr))
print("max_count: " + str(max_count))

index_arr = np.argwhere(n_obs_per_px_arr > 0)
num_pixels = len(index_arr)
print("num_pixels: " + str(num_pixels))


#Calculates the variavility timeline map.
# Y = pixel_idx, represents a coordinate.
# X = sample_idx, represents an energy value

variability = np.zeros((num_pixels, max_count))
sample_num_arr = np.zeros((num_pixels, max_count))
pixel_idx_dic = {}
pixel_coords_dic = {}
sample_count_arr = np.tile(np.nan, (MAX_DEC, MAX_RA))
total_sample_count = 0

for i in range(0, n_samples):

    coords = coords_arr[i]
    energy = lcHelper.get_sum_of_energies(lc[i,:])

    sample_idx = 0
    if not np.isnan(sample_count_arr[coords["dec"], coords["ra"]]):
        sample_idx = int(sample_count_arr[coords["dec"], coords["ra"]])

    if energy > MIN_ENERGY: # or sample_idx > 0:

        # If we have key get the value, else assign new px_idx and store it
        px_idx = 0
        px_idx_key = str(coords["dec"]) + "-" + str(coords["ra"])

        if px_idx_key in pixel_idx_dic:
            px_idx = pixel_idx_dic[px_idx_key]
            #print(str(px_idx) + " , " + str(sample_idx) + " = " + str(energy))
        else:
            px_idx = int(len(pixel_idx_dic))
            pixel_idx_dic[px_idx_key] = px_idx
            pixel_coords_dic[px_idx] = coords

        variability[px_idx, sample_idx] = energy
        sample_num_arr[px_idx, sample_idx] = i
        total_sample_count += 1

        if sample_idx > 0:
            sample_count_arr[coords["dec"], coords["ra"]] += 1
        else:
            sample_count_arr[coords["dec"], coords["ra"]] = 1


# Change scale range to 0..255 and sqrt
#variability = (variability / np.max(variability)) * 255

# Remove rows with only one energy stored
rows_to_remove = []
real_max_count = 0
for px_idx in range(0, len(variability[:, 0])):
    if px_idx in pixel_coords_dic:
        coords = pixel_coords_dic[px_idx]
        sample_count = int(sample_count_arr[coords["dec"], coords["ra"]])
        if np.mean(variability[ px_idx, 0:sample_count ]) <  MIN_ENERGY:
            rows_to_remove.append(px_idx)
        else:
            real_max_count = max(sample_count, real_max_count)

# Crop variability map, remove rows and not used columns at the end
variability = np.delete(variability, rows_to_remove, 0)
variability = np.delete(variability, range(real_max_count, max_count), 1)
#variability[variability == 0] = 255 # Invert background
sample_num_arr = np.delete(sample_num_arr, rows_to_remove, 0)
sample_num_arr = np.delete(sample_num_arr, range(real_max_count, max_count), 1)


# Plot the variability
plt.imshow(variability)
plt.colorbar()
plt.show()

# Lines plot
for px_idx in range(0, len(variability[:, 0])):
    plt.plot(variability[ px_idx, : ])

plt.show()

# Prepare data to be saved as CSV
n_cols = consts.LC_NUM_CHANNELS + 4 # ra, dec, time, channels, total
out_data = np.zeros((total_sample_count, n_cols))
n_rows = 0
offset = PIX_SIZE/2

for px_idx in range(0, len(variability[:, 0])):

    if px_idx in pixel_coords_dic:
        coords = pixel_coords_dic[px_idx]
        max = int(sample_count_arr[coords["dec"], coords["ra"]])

        for sample_idx in range(0, min(max, len(sample_num_arr[px_idx, :]))):
            i = int(sample_num_arr[px_idx, sample_idx])
            energy = variability[px_idx, sample_idx]

            if energy > MIN_ENERGY:
                out_data[n_rows, 0] = (coords["ra"] * PIX_SIZE) + offset
                out_data[n_rows, 1] = (coords["dec"] * PIX_SIZE) + offset
                out_data[n_rows, 2] = lc[i, consts.LC_TIME_COL]
                for j in range(0, consts.LC_NUM_CHANNELS):
                    out_data[n_rows, 3 + j] = lc[i, consts.LC_FIRST_CHANNEL_COL + j]
                out_data[n_rows, n_cols - 1] = energy

                n_rows += 1

out_data = np.delete(out_data, range(n_rows, total_sample_count), 0) # Remove unused rows

np.savetxt("../variability/pixSize" + str(PIX_SIZE) + "/variability.csv", out_data, delimiter=",", fmt='%10.6f', header='RA, Dec, Time, Ch0, Ch1, Ch2, Ch3, Ch4, Ch5, Ch6, Ch7, Total')
