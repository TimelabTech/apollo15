#!/usr/bin/python
# -*- coding: utf-8 -*-

# ALLSKY FITS GENERATOR
# ===============================================
# Author: Ricardo Vallés Blanco (ESAC)
#
# The following code reads a ligthcurve and an
# attitude file and generates an all sky image
# of high resolution that later is exported to
# WCS Fits Images in order to use them as an input
# of Aladin Desktop
#
# ALGORITHM STEPS:
# 1 - Calculates the GTIs excluding when the Sun is inside the FOV
# 2 - Loads the ligthcurve and removes the data outside GTIs
# 3 - Loads the attitude data
# 4 - Define output image size
# 5 - Prepare allsky´s energy and exposure data arrays
# 6 - Project each observation over the energy and exposure data arrays
#       6.1 - Compute the observed energy for a given channels range
#             and an observation time.
#       6.2 - Get the coordinates for a given observation time. The coordinates
#             are calculated with linear interpolation.
#       6.3 - Proyect on the energy map summing the observed energy multiplied
#             by each element of the Map of Relative Source Contributions(MRSC).
#             Also the MRSC is projected over the exposure map
# 7 - Calculate the final flux data array by dividing each element of the
#     energy map by the corresponding element of the exposure map.
#     Weighted Average: sum(Wxy * Xxy)/sum(Wxy)
#                   Or: sum(exposureMap[x,y] * energyMap[x,y])/sum(exposureMap[x,y])
# 8 - Get the maximun computed flux
# 9 - Use the maximun flux to calibrate all flux values in the range 0..255
# 10- Show plots
# 11- Get generated flux image and split in N images and save each one in a
#     WCS Fits Image file.

import os
import numpy as np
from utils import ligthcurve_helper as lcHelper
from utils import attitude_helper as attHelper
from utils import img_helper as imgHelper
from utils import hist
from utils import gti as gtiHelper
import matplotlib
import matplotlib.pyplot as plt
import constants as consts

# Calculates the GTIs including the Sun is outside the FOV
solar_gtis = lcHelper.get_gtis_from_file(consts.TP_SOLAR_FILE,
                                        consts.TP_SOLAR_THRESHOLD)

gtis = gtiHelper.cross_gtis([solar_gtis, consts.GTIS])

# Loads the ligthcurve and removes the data outside GTIs
lc = lcHelper.get_ligthcurve(consts.LC_FILE)
lc = lcHelper.filter_by_gti(lc, gtis)

# Loads the attitude data
att = attHelper.load_attitude(consts.ATT_FILE)

print ("- Input data is ready.")

# Define output image size
height = int(180.0 * consts.IMG_SCALE) # 180 from Declination range
width = int(360.0 * consts.IMG_SCALE) # 360 from Right Ascension range

# Prepare allsky´s energy and exposure data arrays
img_total_energy_map = np.zeros((height, width))
img_exposure_map = np.zeros((height, width))

# Draw each observation on its location inside the energy and exposure maps
for i in range(0, len(lc[:, 0])):

    energy = lcHelper.get_sum_of_energies(lc[i,:])

    coords = attHelper.get_ra_dec(lc[i, consts.LC_TIME_COL], att)
    ra_int = int(coords[0] * consts.IMG_SCALE)
    dec_int = int((coords[1] + 90.0) * consts.IMG_SCALE)

    img_total_energy_map = imgHelper.drawFOV(ra_int, dec_int, energy,
                                            img_total_energy_map,
                                            exposure_map=img_exposure_map)

print ("- Energy and exposure data ready, preparing flux map.")

# Calculates the final flux map image
img_flux_map = np.zeros((height, width))
for dec in range(0, height):
    for ra in range(0, width):
        if img_exposure_map[dec, ra] > consts.MIN_EXPOSURE:
            img_flux_map[dec, ra] = img_total_energy_map[dec, ra] / img_exposure_map[dec, ra]

# Calculates the max flux
max_flux = np.max(img_flux_map)

# Calibrate each pixel value in range 0..255
for dec in range(0, height):
    for ra in range(0, width):
        if img_flux_map[dec, ra] > 0:
            img_flux_map[dec, ra] = int((img_flux_map[dec, ra] / max_flux) * consts.COLORS)


# Show Expousure, Energy, Flux and Equalized data plots
# =====================================================

plt.title("Exposure Map")
plt.imshow(img_exposure_map)
plt.colorbar()
plt.annotate('SCO X-1', xy=(244.979 * consts.IMG_SCALE, (-15.640 + 90) * consts.IMG_SCALE),
             xycoords='data', xytext=(0.5, 0.5), textcoords='figure fraction',
             arrowprops=dict(arrowstyle="->"))
plt.annotate('Cyg X-1', xy=(299.59 * consts.IMG_SCALE, (35.20 + 90) * consts.IMG_SCALE),
             xycoords='data', xytext=(0.75, 0.75), textcoords='figure fraction',
             arrowprops=dict(arrowstyle="->"))
plt.show()


plt.title("Energy Map")
plt.imshow(img_total_energy_map)
plt.colorbar()
plt.show()


plt.title("All Sky Plot")
plt.imshow(img_flux_map)
plt.colorbar()
plt.show()


#Img equalization
if const.EQUALIZE_IMAGE:
    eq_img = hist.histeq(img_flux_map)

    plt.title("All Sky Equalized Plot")
    plt.imshow(eq_img)
    plt.colorbar()
    plt.show()


# Extract clipped images and save as Fits Images
# =====================================================
if const.WRITE_FITS_FILES:
    clip_angle = 4 # Half (radious, not diameter) of the clipped images´s size in degrees
    clip_angle2 = clip_angle * 2 # Total angular size of the clipped image
    scaled_clip_angle = clip_angle * consts.IMG_SCALE
    deg_px_ratio = (1.0 + 0.1)/consts.IMG_SCALE # 0.1 for overlaying margin (for Aladin HiPS Gen)

    # Clip images and save as Fits
    for dec in xrange(clip_angle, 180, clip_angle2):
        for ra in xrange(clip_angle, 360, clip_angle2):
            ra_int = int(ra * consts.IMG_SCALE)
            dec_int = int(dec * consts.IMG_SCALE)

            clipped_img = np.array(eq_img[ dec_int - scaled_clip_angle : dec_int + scaled_clip_angle,
                                   ra_int - scaled_clip_angle : ra_int + scaled_clip_angle ], dtype=np.uint8)

            avg = int(np.average(clipped_img))
            min = int(np.min(clipped_img))
            max = int(np.max(clipped_img))

            #FILENAME: /DEC_RA_AVG_MIN_MAX.fits
            filename = consts.OUTPUT_FOLDER + 'fits_' + str(dec) + '_' + str(ra) + '_' + str(avg) + '_' + str(min) + '_' + str(max) + '.fits'
            imgHelper.saveImage (clipped_img, ra, dec - 90, deg_px_ratio, filename)
