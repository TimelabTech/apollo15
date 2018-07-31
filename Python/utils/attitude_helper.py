
import numpy as np
import constants as consts

def load_attitude (filePath):
    return np.loadtxt(filePath,
                    comments="#",
                    delimiter=",",
                    skiprows=consts.ATT_HEADER_ROWS,
                    #converters = {consts.ATT_RA_COL: lambda s: 360.0 * (float(s.strip() or 0) / 24.0)},  #Convert hours to degrees
                    usecols = (consts.ATT_TIME_COL, consts.ATT_RA_COL, consts.ATT_DEC_COL))


# Returns the ra dec interpolated for a given time
def get_ra_dec(time, att):

    #print("time: " + str(time))

    att_times = att[:,0]

    idx = (np.abs(att_times - time)).argmin()

    if (att[idx, 0] > time) and (idx > 0):
        idx -= 1

    f_time = att[idx, 0]
    ra = att[idx, 1]
    dec = att[idx, 2]

    #print("time found: " + str(f_time) + " ra: " + str(ra) + " dec: " + str(dec))

    if (f_time < time) and (idx < len(att_times) - 1):

        t_inc = att[idx + 1, 0] - f_time
        t_inc2 = time - f_time
        ratio = t_inc2 / t_inc

        #print("t_inc: " + str(t_inc))
        #print("ratio: " + str(ratio))

        f_time = f_time + (t_inc * ratio)
        ra = ra + ((att[idx + 1, 1] - ra) * ratio)
        dec = dec + ((att[idx + 1, 2] - dec) * ratio)

    """elif (f_time > time) and (idx > 0):

        t_inc = f_time - att[idx - 1, 0]
        t_inc2 = f_time - time
        ratio = t_inc2 / t_inc

        print("t_dec: " + str(t_inc))
        print("ratio: " + str(ratio))

        f_time = f_time - (t_inc * ratio)
        ra = ra + ((ra - att[idx - 1, 1]) * ratio)
        dec = dec + ((dec - att[idx - 1, 2]) * ratio)"""


    #print(str([ ra, dec, f_time ]) + " - " + str(tmp_time) + " ... " + str(att[idx, 0]))
    return [ ra, dec ]
