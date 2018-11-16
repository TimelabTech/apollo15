import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from astropy.io import fits

hdu_list = fits.open("../../HST/u2c70104t/u2c70104t_c0f.fits")
hdu_list.info()

image_data = hdu_list[0].data

print(type(image_data))
print(image_data.shape)

#header = hdu_list['PRIMARY'].header
#print(header)

print('Min:', np.min(image_data[0]))
print('Max:', np.max(image_data[0]))
print('Mean:', np.mean(image_data[0]))
print('Stdev:', np.std(image_data[0]))

#plt.imshow(image_data[1], cmap='gray')
#plt.colorbar()

#NBINS = 1000
#histogram = plt.hist(image_data[0].flat, NBINS)
#plt.show()

plt.imshow(image_data[0], cmap='gray', norm=LogNorm())

# I chose the tick marks based on the histogram above
cbar = plt.colorbar(ticks=[0,200,400])
cbar.ax.set_yticklabels(['0','200','400'])

plt.show()
