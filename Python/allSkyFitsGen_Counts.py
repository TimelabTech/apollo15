#!/usr/bin/python
# -*- coding: utf-8 -*-

# ALLSKY FITS GENERATOR BASED IN COUNTS
# ===============================================
# Author: Ricardo Vallés Blanco (Timelab Technologies)
#
# The following code reads a ligthcurve and an
# attitude file and generates an all sky image
# of high resolution based in the lightcurve counts
# that later is exported to WCS Fits Images in order
# to use them as an input for Aladin Desktop
#
# ALGORITHM STEPS:
# 0-  Get image scale and scale MRSC array by the scale and the degrees
#     per MRSC element factors. The scaling is based on biliniar interpolation.
# 1 - Calculates the GTIs excluding when the Sun is inside the FOV
# 2 - Loads the ligthcurve and removes the data outside GTIs
# 3 - Loads the attitude data
# 4 - Define output image size
# 5 - Prepare allsky´s counts and exposure data arrays
# 6 - Project each observation over the counts and exposure data arrays
#       6.1 - Compute the observed total counts for a given channels range
#             and an observation time. This means that for a given time,
#             if the detector is in a supported mode, then the total counts
#             are the sum of the background substracted counts of each channel
#             inside the given channel range.
#       6.2 - Get the coordinates for a given observation time. The coordinates
#             are calculated with linear interpolation.
#       6.3 - Proyect on the counts map summing the observed total counts multiplied
#             by each element of the Map of Relative Source Contributions(MRSC).
#             Also the MRSC is projected over the exposure map
# 7 - Calculate the computed counts array by dividing each element of the
#     counts map by the corresponding element of the exposure map.
#     Weighted Average: sum(Wxy * Xxy)/sum(Wxy)
#                   Or: sum(exposureMap[x,y] * countsMap[x,y])/sum(exposureMap[x,y])
#
#     Note:
#     After executing steps 6.3 and 7, the values on the computed counts map are
#     the wheigted average all total counts overlaped due the projection of the FOV
#     over all the sky, using as weights the values of the MRSC divided by 100 in
#     order to get the percentage ratio.
#
# 8 - Get the minumum and maximun computed counts
# 9 - Use the minumum and maximun counts to calibrate all computed counts values
#     in the range 0..255
# 10- Show plots
# 11- Get generated computed counts image and split in a grid of images and save each one in a
#     WCS Fits Image file. The image width and height is 8 degrees. And its the top-left
#     corner RA and Dec of the images fall in the multiples of 8 until 360 for RA,
#     and 180 for Dec
#
#     Note: All the Dec (Declination) values in the algorithm has added 90 to work in
#     range 0..180 instead of -90..90 in order to be able to use them as array indices

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
img_total_counts_map = np.zeros((height, width))
img_exposure_map = np.zeros((height, width))

# Draw each observation on its location inside the counts and exposure maps
for i in range(0, len(lc[:, 0])):

    counts = lcHelper.get_total_counts(lc[i,:])  # get_sum_of_energies

    if counts >= consts.MIN_COUNTS and counts != 0:
        coords = attHelper.get_ra_dec(lc[i, consts.LC_TIME_COL], att)
        ra_int = int(coords[0] * consts.IMG_SCALE)
        dec_int = int((coords[1] + 90.0) * consts.IMG_SCALE)

        img_total_counts_map = imgHelper.drawFOV(ra_int, dec_int, counts,
                                                img_total_counts_map,
                                                exposure_map=img_exposure_map)

print ("- Counts and exposure data ready, preparing computed counts map.")

# Calculates the computed counts map image
img_comp_counts_map = np.zeros((height, width))
for dec in range(0, height):
    for ra in range(0, width):
        if img_exposure_map[dec, ra] > consts.MIN_EXPOSURE:
            img_comp_counts_map[dec, ra] = img_total_counts_map[dec, ra] / img_exposure_map[dec, ra]

# Calculates the min and max computed counts
min_flux = np.min(img_comp_counts_map)
max_flux = np.max(img_comp_counts_map)

# Calibrate each pixel value in range 0..255
for dec in range(0, height):
    for ra in range(0, width):
        img_comp_counts_map[dec, ra] = int(((img_comp_counts_map[dec, ra] - min_flux) / max_flux) * consts.COLORS)



# Show Expousure, Counts, Computed Counts and Equalized data plots
# =====================================================
if consts.SHOW_PLOTS:
    
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


    plt.title("Counts Map")
    plt.imshow(img_total_counts_map)
    plt.colorbar()
    plt.show()


    plt.title("All Sky Plot")
    plt.imshow(img_comp_counts_map)
    plt.colorbar()
    plt.show()


#Img equalization
if consts.EQUALIZE_IMAGE:
    img_comp_counts_map = hist.histeq(img_comp_counts_map)

    plt.title("All Sky Equalized Plot")
    plt.imshow(img_comp_counts_map)
    plt.colorbar()
    plt.annotate('SCO X-1', xy=(244.979 * consts.IMG_SCALE, (-15.640 + 90) * consts.IMG_SCALE),
                 xycoords='data', xytext=(0.5, 0.5), textcoords='figure fraction',
                 arrowprops=dict(arrowstyle="->"))
    plt.annotate('Cyg X-1', xy=(299.59 * consts.IMG_SCALE, (35.20 + 90) * consts.IMG_SCALE),
                 xycoords='data', xytext=(0.75, 0.75), textcoords='figure fraction',
                 arrowprops=dict(arrowstyle="->"))
    plt.show()


# Extract clipped images and save as Fits Images
# =====================================================
if consts.WRITE_FITS_FILES:
    clip_angle = 4 # Half (radious, not diameter) of the clipped images´s size in degrees
    clip_angle2 = clip_angle * 2 # Total angular size of the clipped image
    scaled_clip_angle = clip_angle * consts.IMG_SCALE
    deg_px_ratio = (1.0 + 0.1)/consts.IMG_SCALE # 0.1 for overlaying margin (for Aladin HiPS Gen)

    # Clip images and save as Fits
    for dec in xrange(clip_angle, 180, clip_angle2):
        for ra in xrange(clip_angle, 360, clip_angle2):
            ra_int = int(ra * consts.IMG_SCALE)
            dec_int = int(dec * consts.IMG_SCALE)

            clipped_img = np.array(img_comp_counts_map[ dec_int - scaled_clip_angle : dec_int + scaled_clip_angle,
                                   ra_int - scaled_clip_angle : ra_int + scaled_clip_angle ], dtype=np.uint8)

            avg = int(np.average(clipped_img))
            min = int(np.min(clipped_img))
            max = int(np.max(clipped_img))

            #FILENAME: /DEC_RA_AVG_MIN_MAX.fits
            filename = consts.OUTPUT_FOLDER + 'fits_' + str(dec) + '_' + str(ra) + '_' + str(avg) + '_' + str(min) + '_' + str(max) + '.fits'
            imgHelper.saveImage (clipped_img, ra, dec - 90, deg_px_ratio, filename)
