#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import scipy.misc
from astropy.io import fits
from astropy.wcs import WCS
import utils.exception_helper as ExHelper
import constants as consts

MAX_W = (360 * consts.IMG_SCALE)
MAX_H = (180 * consts.IMG_SCALE)
FOV_SCALE = consts.FOV/len(consts.MRSC) # Degress per pixel scale


# Scale the MRSC array with bicubic interpolation
consts.MRSC = np.array(consts.MRSC, dtype=np.uint8)
consts.MRSC = scipy.misc.imresize(consts.MRSC, FOV_SCALE * consts.IMG_SCALE, interp='bicubic')
MRSC_SIZE = len(consts.MRSC)
MRSC_CENTER = int(MRSC_SIZE/2)


# drawFOV: Projects value (energy or counts..) over the image data using the MRSC data
#          in a given coordinates. Also upadates the exposure_map if passed
def drawFOV (ra, dec, value, img_data, exposure_map):

    for ra_inc in range(0, MRSC_SIZE):
        for dec_inc in range(0, MRSC_SIZE):

            ratio = consts.MRSC[dec_inc][ra_inc] / 100.0
            if ratio > 0:

                f_ra = int((ra + (ra_inc - MRSC_CENTER)) % MAX_W)
                f_dec = int((dec + (dec_inc - MRSC_CENTER)) % MAX_H)

                img_data[f_dec, f_ra] += (value * ratio)
                exposure_map[f_dec, f_ra] += ratio

    return img_data


# Saves an image as FITS with WCS information
def saveImage (imageData, ra, dec, scale, fileName):

    try:
        # Initialize WCS information
        wcs = WCS(naxis=2)

        # Use the center of the image as projection center
        wcs.wcs.crpix = [imageData.shape[1] / 2. + 0.5,
                         imageData.shape[0] / 2. + 0.5]

        # Set the coordinates of the image center
        wcs.wcs.crval = [ra, dec] # Aladin RA goes from 0 to 360 (for J2000)

        # Set the pixel scale (in deg/pix)
        wcs.wcs.cdelt = [scale, scale]

        # Set the coordinate system
        wcs.wcs.ctype = ['RA---CAR', 'DEC--CAR'] # ['GLON-CAR', 'GLAT-CAR'] # ra, dec

        # And produce a FITS header
        header = wcs.to_header()

        #Avoid transparent color in Aladin HipsGen
        if consts.GEN_ALADIN_READY_FITS:
            imageData[imageData < 1] = 1

        # We can also just output one of the wavelengths
        fits.writeto(fileName, imageData, header=header, clobber=True)

        print('Saved: ' + fileName)

    except:
        print(ExHelper.getException('saveImage'))
