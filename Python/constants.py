#!/usr/bin/python
# -*- coding: utf-8 -*-


#====================================
# X-ray ligthcurves section
#====================================

# Path of the file with the ligthcurve (time and counts) data in csv format
LC_FILE = "../Data/Be.dat"

# Good time intervals: [[start_1, end_1], ... ,[start_N, end_N]]
GTIS = [[224.0, 288.0]]
        #  Cyg X-1 TimeRange: [[246.444977, 247.599548]];
        #  Sco X-1 TimeRange: [[245.881012, 246.342789],[274.126343, 287.586243]]

# Time column index in the lc file
LC_TIME_COL = 0

# Duration of each observation (count) in seconds
LC_TIME_BIN = 8

# Flag or detector mode column index in the lc file
LC_FLAG_COL = 1

# Index of the column with the first channel data in the lc file. Next channels must be consecutives.
LC_FIRST_CHANNEL_COL = 2

# Number of channel´s data columns in the lc file
LC_NUM_CHANNELS = 8

# Note: Customize LC_FIRST_CHANNEL_COL and LC_NUM_CHANNELS in order to create
#       AllSky Fits for only one channel, or different channel ranges.

# Background data array, one element per channel
LC_BACKGROUND = [ 69.38, 20.14, 28.76, 35.45, 32.90, 36.42, 32.86, 139.92 ]



#====================================
# XRFS Instrument section
#====================================

# Field of view of the instrument, (MRSC width in degrees)
FOV = 56.0

# Value in the flag or detector mode column for defining the normal operation mode (Only for energy based sky)
NORMAL_MODE = 16

# Value in the flag or detector mode column for defining the extended operation mode (Only for energy based sky)
EXTENDED_MODE = 144

# The channel energy will be multiplied by this factor if in extended mode (Only for energy based sky)
EXTENDED_MODE_FACTOR = 2.0

# Channel energies array, one element per channel. (Only for energy based sky)
# Average of paper ranges in keV, from:
# https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_data/ldp/xray_spectrometer/
CHANNEL_ENERGIES = [ 0.90, 1.18, 1.45, 1.75, 2.05, 2.32, 2.60, 3.50 ]

# Read only data from NORMAL_MODE, from EXTENDED_MODE or both.
SUPPORTED_MODES = [ NORMAL_MODE, EXTENDED_MODE ]

# Minimum total counts after substracting background data. Values below this will be dismissed.
MIN_COUNTS = -150

# Map of Relative Source Contributions
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
# Attitude data section
#====================================

# Path of the file with the attitude data (time, RA, Dec) in csv format
ATT_FILE = "../Data/XrayINS-RA_DEC.txt"

# Number of header rows in the attitude file
ATT_HEADER_ROWS = 2

# Time column index in the attitude file
ATT_TIME_COL = 0

# RA (Rigth ascension) column index in the attitude file
ATT_RA_COL = 1

# Dec (Declination) column index in the attitude file
ATT_DEC_COL = 2



#====================================
# BODY-Theta_Phi files section
#====================================

# Path of the file with the sun position data (GET(Time)[h], theta[deg], phi[deg]) in csv format
TP_SOLAR_FILE = "../Data/Sun-theta_phi.txt"

# With solar angles below this threshold will be dissmised
TP_SOLAR_THRESHOLD = 32.0



#====================================
# Image generation section
#====================================

# Path of the output folder for writing the All Sky Fits. Must exist
OUTPUT_FOLDER = "../output/HiPS_RGB/Apollo15_XRFS_Be_AllSkyFits_Channels7_8_EQ/"

# Sets the resolution of the output image -> Scale * (360x180)px
IMG_SCALE = 4

# Sets the color scale range. Must be 255 if using equalization.
COLORS = 255.0

# Sets the miminum exposure to compute the weighted average over one pixel
MIN_EXPOSURE = 1.0

# Show plots after computing the all sky data
SHOW_PLOTS = True

# Equalize all sky image before exporting to Fits files
EQUALIZE_IMAGE = True

# If True writes the all sky image as Fits files in the output folder
WRITE_FITS_FILES = True

# If True replaces the zeros by ones in the Fits files data to avoid transparent color in Aladin HipsGen
GEN_ALADIN_READY_FITS = True
