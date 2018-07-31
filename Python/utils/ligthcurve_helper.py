import numpy as np
import bisect
import constants as consts

def get_ligthcurve(path):
    return np.loadtxt(path)


# Multiplies the counts of a specified channel by the energy related to this channel.
def get_energy(channel_col, lc_row, avg_count_arr):
    energy = 0

    if (lc_row[consts.LC_FLAG_COL] == consts.NORMAL_MODE \
        or lc_row[consts.LC_FLAG_COL] == consts.EXTENDED_MODE) \
        and lc_row[channel_col] > 0:

        ch_idx = channel_col - consts.LC_FIRST_CHANNEL_COL
        avg_ch_energy = avg_count_arr[ch_idx] * consts.CHANNEL_ENERGIES[ch_idx]
        energy = (lc_row[channel_col] * consts.CHANNEL_ENERGIES[ch_idx]) - avg_ch_energy

        if energy < 0:
            return 0

        if lc_row[consts.LC_FLAG_COL] == consts.EXTENDED_MODE:
            energy *= consts.EXTENDED_MODE_FACTOR  # Detector is in exetended mode

    return energy


# Gets the sum of the energies of all channels
def get_sum_of_energies(lc_row, avg_count_arr):

    sum_of_energies = 0
    for channel in range(consts.LC_FIRST_CHANNEL_COL, consts.LC_FIRST_CHANNEL_COL + consts.LC_NUM_CHANNELS):
        sum_of_energies += get_energy(channel, lc_row, avg_count_arr)

    return sum_of_energies


# Gets the sum of the energies of all channels
def get_channels_avg_count(lc):

    avg_count_arr = np.zeros(consts.LC_NUM_CHANNELS)
    for channel in range(consts.LC_FIRST_CHANNEL_COL, consts.LC_FIRST_CHANNEL_COL + consts.LC_NUM_CHANNELS):
        avg_count_arr[channel - consts.LC_FIRST_CHANNEL_COL] = np.average(lc[:, channel])

    return avg_count_arr


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