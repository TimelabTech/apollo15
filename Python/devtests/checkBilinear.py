#!/usr/bin/python
# -*- coding: utf-8 -*-

# Check the quality after the scaling of the MRSC

import numpy as np
import scipy.misc
import matplotlib
import matplotlib.pyplot as plt
import constants as consts

consts.MRSC = np.array(consts.MRSC, dtype=np.uint8)

plt.imshow(consts.MRSC)
plt.show()

consts.MRSC = scipy.misc.imresize(consts.MRSC, consts.IMG_SCALE * 1.0, interp='bicubic')

plt.imshow(consts.MRSC)
plt.show()
