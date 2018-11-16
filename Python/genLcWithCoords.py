#!/usr/bin/python
# -*- coding: utf-8 -*-

# Creates a CSV file with the data of the LC FILE plus coordinates
# and total energy columns
# Author: Ricardo Vallés Blanco (ESAC)

import numpy as np
from utils import ligthcurve_helper as lcHelper
from utils import attitude_helper as attHelper
import constants as consts


lc = lcHelper.get_ligthcurve(consts.LC_FILE)
att = attHelper.load_attitude(consts.ATT_FILE)

n_samples = len(lc[:, 0])

N = len(lc[0, :])
result = np.zeros((n_samples, N+3))
result[:,:-3] = lc

for i in range(0, n_samples):
    time = lc[i, 0]
    coords = attHelper.get_ra_dec(time, att)

    total_energy = lcHelper.get_sum_of_energies(lc[i,:])

    result[i, -3] = total_energy
    result[i, -2] = coords[0]
    result[i, -1] = coords[1]

np.savetxt("../variability/lcBeWithCoords.csv", result, delimiter=",", fmt='%10.6f', header='Time, Mode, Ch0, Ch1, Ch2, Ch3, Ch4, Ch5, Ch6, Ch7, Total, RA, DEC')
