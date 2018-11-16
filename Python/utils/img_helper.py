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


# drawFOV: Projects an energy value over the image data using the MRSC data
#          in a given coordinates. Also upadates the exposure_map if passed
def drawFOV (ra, dec, energy, img_data, exposure_map=None):

    for ra_inc in range(0, MRSC_SIZE):
        for dec_inc in range(0, MRSC_SIZE):

            ratio = consts.MRSC[dec_inc][ra_inc]
            if ratio > 0:

                f_ra = int((ra + (ra_inc - MRSC_CENTER)) % MAX_W)
                f_dec = int((dec + (dec_inc - MRSC_CENTER)) % MAX_H)

                img_data[f_dec, f_ra] += (energy * ratio)

                if not exposure_map is None:
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
        #wcs.wcs.crval = [233.4452, 1.2233]
        wcs.wcs.crval = [ra, dec] # Aladin RA goes from -180 to 180
        #print('Coords: ' + str(wcs.wcs.crval))

        # Set the pixel scale (in deg/pix)
        # scale = 0.1 #1.0 / consts.IMG_SCALE # np.degrees(3. * pc / imageData.shape[0] / image.distance)
        wcs.wcs.cdelt = [scale, scale]
        #print('Cdelt: ' + str(wcs.wcs.cdelt))

        # Set the coordinate system
        wcs.wcs.ctype = ['GLON-CAR', 'GLAT-CAR'] # ra, dec

        # And produce a FITS header
        header = wcs.to_header()

        #Avoid transparent color in Aladin HipsGen
        imageData[imageData < 1] = 1

        # We can also just output one of the wavelengths
        fits.writeto(fileName, imageData, header=header, clobber=True)

        print('Saved: ' + fileName)

    except:
        print(ExHelper.getException('saveImage'))
