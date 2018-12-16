import numpy as np
import bisect
import constants as consts

def get_ligthcurve(path):
    return np.loadtxt(path)

# Returns the background corrected total counts
def get_total_counts(lc_row):

    total_counts = 0

    if lc_row[consts.LC_FLAG_COL] in consts.SUPPORTED_MODES:

        for channel in range(consts.LC_FIRST_CHANNEL_COL,
                            consts.LC_FIRST_CHANNEL_COL + consts.LC_NUM_CHANNELS):

            counts = lc_row[channel]
            if counts > 0:
                ch_idx = channel - consts.LC_FIRST_CHANNEL_COL
                corrected_counts = counts - consts.LC_BACKGROUND[ch_idx]
                total_counts += corrected_counts

    return total_counts


# Multiplies the counts of a specified channel by the energy related to this channel.
def get_energy(channel_col, lc_row):
    energy = 0

    if lc_row[consts.LC_FLAG_COL] in consts.SUPPORTED_MODES \
        and lc_row[channel_col] > 0:

        ch_idx = channel_col - consts.LC_FIRST_CHANNEL_COL
        real_counts = lc_row[channel_col] - consts.LC_BACKGROUND[ch_idx]
        if real_counts <= consts.MIN_COUNTS:
            return 0

        energy = (real_counts * consts.CHANNEL_ENERGIES[ch_idx]) / consts.LC_TIME_BIN

        if energy <= 0:
            return 0

        if lc_row[consts.LC_FLAG_COL] == consts.EXTENDED_MODE:
            energy *= consts.EXTENDED_MODE_FACTOR  # Detector is in exetended mode

    return energy


# Gets the sum of the energies of all channels
def get_sum_of_energies(lc_row):

    sum_of_energies = 0
    for channel in range(consts.LC_FIRST_CHANNEL_COL,
                        consts.LC_FIRST_CHANNEL_COL + consts.LC_NUM_CHANNELS):
        sum_of_energies += get_energy(channel, lc_row)

    return sum_of_energies


# Finds the idx of the nearest value on the array, array must be sorted
def find_idx_nearest_val(array, value):

    # idx = np.searchsorted(array, value, side="left")
    idx = bisect.bisect_left(array, value) # Looks like bisec is faster with structured data than searchsorted

    if idx >= len(array):
        idx_nearest = len(array) - 1
    elif idx == 0:
        idx_nearest = 0
    else:
        if abs(value - array[idx - 1]) < abs(value - array[idx]):
            idx_nearest = idx - 1
        else:
            idx_nearest = idx
    return idx_nearest


# Returns a lightcurve filtered by gtis
def filter_by_gti(lc, gtis, time_column=0):

    flt_lc = np.array([]).reshape((0, lc.shape[1]))
    start_event_idx = 0
    end_event_idx = 0

    for gti_index in range(len(gtis)):

        start = gtis[gti_index][0]
        end = gtis[gti_index][1]

        start_event_idx = find_idx_nearest_val(lc[:, time_column], start)
        if (lc[start_event_idx, time_column] < start and start_event_idx < len(lc) - 1):
            start_event_idx = start_event_idx + 1

        end_event_idx = find_idx_nearest_val(lc[:, time_column], end)
        if (lc[end_event_idx, time_column] > end and end_event_idx > 0):
            end_event_idx = end_event_idx - 1

        if end_event_idx >= start_event_idx:
            flt_lc = np.concatenate((flt_lc, lc[start_event_idx:end_event_idx, :]))

    return flt_lc


# Extracts a GTI array from a BODY-Theta_Phi file with a given threshold
def get_gtis_from_file(path, threshold):

    data = np.loadtxt(path, delimiter=",") # Load the CSV file
    rows = len(data)

    gtis = []
    gtiStart = -1
    gtiEnd = -1

    if rows > 0:
        for i in range(rows):

            time = data[i, 0]
            theta = data[i, 1]

            if theta > threshold:
                # We are inside a GTI
                if gtiStart > 0:
                    gtiEnd = time
                else:
                    gtiStart = time

            elif (gtiStart > 0) and (gtiStart < gtiEnd):
                # We are closing a GTI
                gtis.extend([[gtiStart, gtiEnd]])
                gtiStart = -1
                gtiEnd = -1

    return gtis
