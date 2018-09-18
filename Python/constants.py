
#====================================
# X-ray light curves
#====================================
LC_FILE = "../Data/Be.dat"
GTIS = [[224.0, 277.0], [277.0, 288.0]]
LC_TIME_COL = 0
LC_FLAG_COL = 1
LC_FIRST_CHANNEL_COL = 2
LC_NUM_CHANNELS = 8
LC_BACKGROUND = [ 69.38, 20.14, 28.76, 35.45, 32.90, 36.42, 32.86, 139.92 ]

#====================================
# XRFS Instrument
#====================================
FOV = 30.0
NORMAL_MODE = 16
EXTENDED_MODE = 144
EXTENDED_MODE_FACTOR = 2.0
CHANNEL_ENERGIES = [ 0.90, 1.18, 1.45, 1.75, 2.05, 2.32, 2.60, 3.10 ]  # Average of paper ranges in keV, from: https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_data/ldp/xray_spectrometer/

#Map of Relative Source Contributions
MRSC = [ [  1,  1,  2,  6,  11,  17,  11,  6,  2,  1,  1 ],
         [  1,  2,  4,  9,  15,  23,  15,  9,  4,  2,  1 ],
         [  2,  4,  8, 15,  24,  34,  24, 15,  8,  4,  2 ],
         [  6,  9, 15, 26,  40,  54,  40, 26, 15,  9,  6 ],
         [ 11, 15, 24, 40,  58,  77,  58, 40, 24, 15, 11 ],
         [ 17, 23, 34, 54,  77, 100,  77, 54, 34, 23, 17 ],
         [ 11, 15, 24, 40,  58,  77,  58, 40, 24, 15, 11 ],
         [  6,  9, 15, 26,  40,  54,  40, 26, 15,  9,  6 ],
         [  2,  4,  8, 15,  24,  34,  24, 15,  8,  4,  2 ],
         [  1,  2,  4,  9,  15,  23,  15,  9,  4,  2,  1 ],
         [  1,  1,  2,  6,  11,  17,  11,  6,  2,  1,  1 ] ]


#====================================
# Attitude data
#====================================
ATT_FILE = "../Data/ephemeris_GammaRaySpectrometer_TEC.csv" #"../TEC_A15/TEC_A15_state_point.txt"
ATT_HEADER_ROWS = 2
ATT_TIME_COL = 0
ATT_RA_COL = 25 #29 #7
ATT_DEC_COL = 26 #30 #8


#====================================
# Image generation
#====================================
IMG_SCALE = 3
