#!/usr/bin/python
# -*- coding: utf-8 -*-

# This code plots the Cyg X-1 ligthcurve
# After some analysis I concluded that Cyg X-1 was
# outside or just in the borders of the XRFS FOV.
# The counts received from observed pointining near to Cyg X-1
# are much smaller that the ones coming from SCO X-1
# Author: Ricardo Vallés Blanco (Timelab Technologies)

import numpy as np
from utils import ligthcurve_helper as lcHelper
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as lines


lc = np.loadtxt("../variability/Cyg X-1.csv", delimiter=",")

# Lines plot for each channel and total energy
for col_idx in range(3, len(lc[0, :])):
    plt.plot(lc[ : , col_idx ])

plt.show()

# Draws the energy data from Cyg X-1 vs Sco X-1
lcSco = np.loadtxt("../variability/Sco X-1.csv", delimiter=",")

plt.plot(lc[ : , len(lc[0, :]) - 1 ]) # Blue
plt.plot(lcSco[ : , len(lcSco[0, :]) - 1 ]) # Orange
plt.show()
