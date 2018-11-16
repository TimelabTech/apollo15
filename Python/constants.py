#!/usr/bin/python
# -*- coding: utf-8 -*-

#====================================
# X-ray light curves
#====================================
LC_FILE = "../Data/Be.dat"
GTIS = [[224.0, 288.0]]
        #  Cyg X-1 TimeRange: [[246.444977, 247.599548]];
        #  Sco X-1 TimeRange: [[245.881012, 246.342789],[274.126343, 287.586243]]

LC_TIME_COL = 0
LC_TIME_BIN = 8
LC_FLAG_COL = 1
LC_FIRST_CHANNEL_COL = 2
LC_NUM_CHANNELS = 8
LC_BACKGROUND = [ 69.38, 20.14, 28.76, 35.45, 32.90, 36.42, 32.86, 139.92 ]

#====================================
# XRFS Instrument
#====================================
FOV = 56.0 #  Field of view, (MRSC width in degrees)
NORMAL_MODE = 16
EXTENDED_MODE = 144
EXTENDED_MODE_FACTOR = 2.0
CHANNEL_ENERGIES = [ 0.90, 1.18, 1.45, 1.75, 2.05, 2.32, 2.60, 3.50 ]  # Average of paper ranges in keV, from: https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_data/ldp/xray_spectrometer/

#Map of Relative Source Contributions
# Note: This map has been expanded with three rows/cols per side and was filled
#       with near 0 values in order to smooth the borders
MRSC = [ [  0,  0,  0,  0,  0,  0,  0,   0,   1,   0,  0,  0,  0,  0,  0,  0,  0 ],
         [  0,  0,  0,  0,  0,  0,  0,   3,   3,   3,  0,  0,  0,  0,  0,  0,  0 ],
         [  0,  0,  0,  0,  0,  1,  3,   6,  10,   6,  3,  1,  0,  0,  0,  0,  0 ],
         [  0,  0,  0,  1,  1,  2,  6,  11,  17,  11,  6,  2,  1,  1,  0,  0,  0 ],
         [  0,  0,  1,  1,  2,  4,  9,  15,  23,  15,  9,  4,  2,  1,  1,  0,  0 ],
         [  0,  0,  1,  2,  4,  8, 15,  24,  34,  24, 15,  8,  4,  2,  1,  0,  0 ],
         [  0,  1,  3,  6,  9, 15, 26,  40,  54,  40, 26, 15,  9,  6,  3,  1,  0 ],
         [  0,  3,  6, 11, 15, 24, 40,  58,  77,  58, 40, 24, 15, 11,  6,  3,  0 ],
         [  1,  3, 10, 17, 23, 34, 54,  77, 100,  77, 54, 34, 23, 17, 10,  3,  1 ],
         [  0,  3,  6, 11, 15, 24, 40,  58,  77,  58, 40, 24, 15, 11,  6,  3,  0 ],
         [  0,  1,  3,  6,  9, 15, 26,  40,  54,  40, 26, 15,  9,  6,  3,  1,  0 ],
         [  0,  0,  1,  2,  4,  8, 15,  24,  34,  24, 15,  8,  4,  2,  1,  0,  0 ],
         [  0,  0,  1,  1,  2,  4,  9,  15,  23,  15,  9,  4,  2,  1,  1,  0,  0 ],
         [  0,  0,  0,  1,  1,  2,  6,  11,  17,  11,  6,  2,  1,  1,  0,  0,  0 ],
         [  0,  0,  0,  0,  0,  1,  3,   6,  10,   6,  3,  1,  0,  0,  0,  0,  0 ],
         [  0,  0,  0,  0,  0,  0,  0,   3,   3,   3,  0,  0,  0,  0,  0,  0,  0 ],
         [  0,  0,  0,  0,  0,  0,  0,   0,   1,   0,  0,  0,  0,  0,  0,  0,  0 ] ]


#====================================
# Attitude data
#====================================
ATT_FILE = "../Data/XrayINS-RA_DEC.txt"
ATT_HEADER_ROWS = 2
ATT_TIME_COL = 0
ATT_RA_COL = 1
ATT_DEC_COL = 2


#====================================
# BODY-Theta_Phi files
#====================================
TP_SOLAR_FILE = "../Data/Sun-theta_phi.txt"
TP_SOLAR_THRESHOLD = 30.0


#====================================
# Image generation
#====================================
OUTPUT_FOLDER = "../output/Apollo15_XRFS_Be_AllSkyFits"
IMG_SCALE = 1 # Sets the resolution of the output image -> Scale * (360x180)px
COLORS = 255
MIN_EXPOSURE = 1
EQUALIZE_IMAGE = True
WRITE_FITS_FILES = False
