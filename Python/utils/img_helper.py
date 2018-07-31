
import numpy as np
import constants as consts

MAX_W = (360 * consts.IMG_SCALE)
MAX_H = (180 * consts.IMG_SCALE)

def drawFOV (ra, dec, counts, img_data, max_color=None):

    size = len(consts.MRSC)
    #print ("MRSC Size: " + str(size))

    min = int(-size/2)
    max = int(size/2)

    pixel_size = int(consts.FOV / size)
    #print ("pixel_size: " + str(pixel_size))

    for ra_inc in range(0, size):
        for dec_inc in range(0, size):

            f_ra = int((ra + ((ra_inc + min) * pixel_size * consts.IMG_SCALE)) % MAX_W)
            f_dec = int((dec + ((dec_inc + min) * pixel_size * consts.IMG_SCALE)) % MAX_H)

            realCounts = counts * (consts.MRSC[dec_inc][ra_inc] / 100.0)

            img_data = drawPixel(f_ra, f_dec, realCounts, pixel_size, img_data, max_color)

    return img_data


# Draw a pixel with given size in degrees
def drawPixel (ra, dec, counts, size, img_data, max_color=None):
    size *= consts.IMG_SCALE
    min = int(-size/2)

    for ra_inc in range(0, size):
        for dec_inc in range(0, size):

            f_ra = int((ra + (ra_inc + min)) % MAX_W)
            f_dec = int((dec + (dec_inc + min)) % MAX_H)

            img_data[f_dec, f_ra] += counts
            if max_color and img_data[f_dec, f_ra] > max_color:
                img_data[f_dec, f_ra] = max_color

    return img_data
