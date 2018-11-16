# From https://github.com/StingraySoftware/stingray/blob/master/stingray/gti.py

import numpy as np
import logging
import collections
import copy

def _get_gti_from_extension(lchdulist, accepted_gtistrings=['GTI']):
    hdunames = [h.name for h in lchdulist]
    gtiextn = [ix for ix, x in enumerate(hdunames)
               if x in accepted_gtistrings][0]
    gtiext = lchdulist[gtiextn]
    gtitable = gtiext.data

    colnames = [col.name for col in gtitable.columns.columns]
    # Default: NuSTAR: START, STOP. Otherwise, try RXTE: Start, Stop
    if 'START' in colnames:
        startstr, stopstr = 'START', 'STOP'
    else:
        startstr, stopstr = 'Start', 'Stop'

    gtistart = np.array(gtitable.field(startstr), dtype=np.longdouble)
    gtistop = np.array(gtitable.field(stopstr), dtype=np.longdouble)
    gti_list = np.array([[a, b]
                         for a, b in zip(gtistart,
                                         gtistop)],
                        dtype=np.longdouble)
    return gti_list


def check_gtis(gti):
    """Check if GTIs are well-behaved.

    Check that:

    1. the shape of the GTI array is correct;
    2. no start > end
    3. no overlaps.

    Parameters
    ----------
    gti : list
        A list of GTI ``(start, stop)`` pairs extracted from the FITS file.

    Raises
    ------
    TypeError
        If GTIs are of the wrong shape
    ValueError
        If GTIs have overlapping or displaced values
    """
    gti = np.asarray(gti)
    if len(gti) != gti.shape[0] or len(gti.shape) != 2 or \
            len(gti) != gti.shape[0]:
        raise TypeError("Please check formatting of GTIs. They need to be"
                        " provided as [[gti00, gti01], [gti10, gti11], ...]")

    gti_start = gti[:, 0]
    gti_end = gti[:, 1]

    # Check that GTIs are well-behaved
    if not np.all(gti_end >= gti_start):
        raise ValueError('This GTI end times must be larger than '
                         'GTI start times')

    # Check that there are no overlaps in GTIs
    if not np.all(gti_start[1:] >= gti_end[:-1]):
        raise ValueError('This GTI has overlaps')

    return


def cross_two_gtis(gti0, gti1):
    """Extract the common intervals from two GTI lists *EXACTLY*.

    Parameters
    ----------
    gti0 : iterable of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``
    gti1 : iterable of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``
        The two lists of GTIs to be crossed.

    Returns
    -------
    gtis : ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``
        The newly created GTIs

    See Also
    --------
    cross_gtis : From multiple GTI lists, extract common intervals *EXACTLY*

    Examples
    --------
    >>> gti1 = np.array([[1, 2]])
    >>> gti2 = np.array([[1, 2]])
    >>> newgti = cross_gtis([gti1, gti2])
    >>> np.all(newgti == [[1, 2]])
    True
    >>> gti1 = np.array([[1, 4]])
    >>> gti2 = np.array([[1, 2], [2, 4]])
    >>> newgti = cross_gtis([gti1, gti2])
    >>> np.all(newgti == [[1, 4]])
    True
    """
    gti0 = join_equal_gti_boundaries(np.asarray(gti0))
    gti1 = join_equal_gti_boundaries(np.asarray(gti1))
    # Check GTIs
    check_gtis(gti0)
    check_gtis(gti1)

    gti0_start = gti0[:, 0]
    gti0_end = gti0[:, 1]
    gti1_start = gti1[:, 0]
    gti1_end = gti1[:, 1]

    # Create a list that references to the two start and end series
    gti_start = [gti0_start, gti1_start]
    gti_end = [gti0_end, gti1_end]

    # Concatenate the series, while keeping track of the correct origin of
    # each start and end time
    gti0_tag = np.array([0 for g in gti0_start], dtype=bool)
    gti1_tag = np.array([1 for g in gti1_start], dtype=bool)
    conc_start = np.concatenate((gti0_start, gti1_start))
    conc_end = np.concatenate((gti0_end, gti1_end))
    conc_tag = np.concatenate((gti0_tag, gti1_tag))

    # Put in time order
    order = np.argsort(conc_end)
    conc_start = conc_start[order]
    conc_end = conc_end[order]
    conc_tag = conc_tag[order]

    last_end = conc_start[0] - 1
    final_gti = []
    for ie, e in enumerate(conc_end):
        # Is this ending in series 0 or 1?
        this_series = conc_tag[ie]
        other_series = not this_series

        # Check that this closes intervals in both series.
        # 1. Check that there is an opening in both series 0 and 1 lower than e
        try:
            st_pos = \
                np.argmax(gti_start[this_series][gti_start[this_series] < e])
            so_pos = \
                np.argmax(gti_start[other_series][gti_start[other_series] < e])
            st = gti_start[this_series][st_pos]
            so = gti_start[other_series][so_pos]

            s = np.max([st, so])
        except:  # pragma: no cover
            continue

        # If this start is inside the last interval (It can happen for equal
        # GTI start times between the two series), then skip!
        if s <= last_end:
            continue
        # 2. Check that there is no closing before e in the "other series",
        # from intervals starting either after s, or starting and ending
        # between the last closed interval and this one
        cond1 = (gti_end[other_series] > s) * (gti_end[other_series] < e)
        cond2 = gti_end[other_series][so_pos] < s
        condition = np.any(np.logical_or(cond1, cond2))
        # Well, if none of the conditions at point 2 apply, then you can
        # create the new gti!
        if not condition:
            final_gti.append([s, e])
            last_end = e

    return np.array(final_gti)


def cross_gtis(gti_list):
    """
    From multiple GTI lists, extract the common intervals *EXACTLY*.

    Parameters
    ----------
    gti_list : array-like
        List of GTI arrays, each one in the usual format ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    Returns
    -------
    gti0: 2-d float array
        ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``
        The newly created GTIs

    See Also
    --------
    cross_two_gtis : Extract the common intervals from two GTI lists *EXACTLY*
    """
    gti_list = np.asarray(gti_list)
    for g in gti_list:
        check_gtis(g)

    ninst = len(gti_list)
    if ninst == 1:
        return gti_list[0]

    gti0 = gti_list[0]

    for gti in gti_list[1:]:
        gti0 = cross_two_gtis(gti0, gti)

    return gti0


def get_btis(gtis, start_time=None, stop_time=None):
    """
    From GTIs, obtain bad time intervals, i.e. the intervals *not* covered
    by the GTIs.

    GTIs have to be well-behaved, in the sense that they have to pass
    ``check_gtis``.

    Parameters
    ----------
    gtis : iterable
        A list of GTIs

    start_time : float
        Optional start time of the overall observation (e.g. can be earlier than the first time stamp
        in ``gtis``.

    stop_time : float
        Optional stop time of the overall observation (e.g. can be later than the last time stamp in
        ``gtis``.

    Returns
    -------
    btis : numpy.ndarray
        A list of bad time intervals
    """
    # Check GTIs
    if len(gtis) == 0:
        if not start_time or not stop_time:
            raise ValueError('Empty GTI and no valid start_time '
                             'and stop_time. BAD!')

        return np.asarray([[start_time, stop_time]])
    check_gtis(gtis)

    start_time = assign_value_if_none(start_time, gtis[0][0])
    stop_time = assign_value_if_none(stop_time, gtis[-1][1])

    if gtis[0][0] - start_time <= 0:
        btis = []
    else:
        btis = [[gtis[0][0] - start_time]]
    # Transform GTI list in
    flat_gtis = gtis.flatten()
    new_flat_btis = list(zip(flat_gtis[1:-2:2], flat_gtis[2:-1:2]))
    btis.extend(new_flat_btis)

    if stop_time - gtis[-1][1] > 0:
        btis.extend([[gtis[0][0] - stop_time]])

    return np.asarray(btis)


def gti_len(gti):
    """
    Return the total good time from a list of GTIs.

    Parameters
    ----------
    gti : iterable
        A list of Good Time Intervals

    Returns
    -------
    gti_len : float
        The sum of lengths of all GTIs

    """
    return np.sum([g[1] - g[0] for g in gti])


def check_separate(gti0, gti1):
    """
    Check if two GTIs do not overlap.

    Parameters
    ----------
    gti0: 2-d float array
        List of GTIs of form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    gti1: 2-d float array
        List of GTIs of form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    Returns
    -------
    separate: bool
        ``True`` if GTIs are mutually exclusive, ``False`` if not
    """

    gti0 = np.asarray(gti0)
    gti1 = np.asarray(gti1)
    if len(gti0) == 0 or len(gti1) == 0:
        return True

    # Check if independently GTIs are well behaved
    check_gtis(gti0)
    check_gtis(gti1)

    gti0_start = gti0[:, 0][0]
    gti0_end = gti0[:, 1][-1]
    gti1_start = gti1[:, 0][0]
    gti1_end = gti1[:, 1][-1]

    if (gti0_end <= gti1_start) or (gti1_end <= gti0_start):
        return True
    else:
        return False


def join_equal_gti_boundaries(gti):
    """If the start of a GTI is right at the end of another, join them.

    """
    new_gtis = gti
    touching = gti[:-1, 1] == gti[1:, 0]
    if np.any(touching):
        ng = []
        count = 0
        while count < len(gti) - 1:
            if new_gtis[count, 1] == gti[count + 1, 0]:
                ng.append([gti[count, 0], gti[count + 1, 1]])
            else:
                ng.append(gti[count])
            count += 1
        new_gtis = np.asarray(ng)
    return new_gtis


def append_gtis(gti0, gti1):
    """Union of two non-overlapping GTIs.

    If the two GTIs "touch", this is tolerated and the touching GTIs are
    joined in a single one.

    Parameters
    ----------
    gti0: 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    gti1: 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    Returns
    -------
    gti: 2-d float array
        The newly created GTI

    Examples
    --------
    >>> np.all(append_gtis([[0, 1]], [[2, 3]]) == [[0, 1], [2, 3]])
    True
    >>> np.all(append_gtis([[0, 1]], [[1, 3]]) == [[0, 3]])
    True
    """

    gti0 = np.asarray(gti0)
    gti1 = np.asarray(gti1)

    # Check if independently GTIs are well behaved.
    check_gtis(gti0)
    check_gtis(gti1)

    # Check if GTIs are mutually exclusive.
    if not check_separate(gti0, gti1):
        raise ValueError('In order to append, GTIs must be mutually'
                         'exclusive.')

    new_gtis = np.sort(np.concatenate([gti0, gti1]))

    return join_equal_gti_boundaries(new_gtis)


def join_gtis(gti0, gti1):
    """Union of two GTIs.

    If GTIs are mutually exclusive, it calls ``append_gtis``. Otherwise we put
    the extremes of partially overlapping GTIs on an ideal line and look at the
    number of opened and closed intervals. When the number of closed and opened
    intervals is the same, the full GTI is complete and we close it.

    In practice, we assign to each opening time of a GTI the value ``-1``, and
    the value ``1`` to each closing time; when the cumulative sum is zero, the
    GTI has ended. The timestamp after each closed GTI is the start of a new
    one.

    ::

        (cumsum)   -1   -2         -1   0   -1 -2           -1  -2  -1        0
        GTI A      |-----:----------|   :    |--:------------|   |---:--------|
        FINAL GTI  |-----:--------------|    |--:--------------------:--------|
        GTI B            |--------------|       |--------------------|

    Parameters
    ----------
    gti0: 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    gti1: 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    Returns
    -------
    gti: 2-d float array
        The newly created GTI
    """

    gti0 = np.asarray(gti0)
    gti1 = np.asarray(gti1)

    # Check if independently GTIs are well behaved.
    check_gtis(gti0)
    check_gtis(gti1)

    if check_separate(gti0, gti1):
        return append_gtis(gti0, gti1)

    g0 = gti0.flatten()
    # Opening GTI: type = 1; Closing: type = -1
    g0_type = np.asarray(list(zip(-np.ones(int(len(g0) / 2)),
                                  np.ones(int(len(g0) / 2)))))
    g1 = gti1.flatten()
    g1_type = np.asarray(list(zip(-np.ones(int(len(g1) / 2)),
                                  np.ones(int(len(g1) / 2)))))

    g_all = np.append(g0, g1)
    g_type_all = np.append(g0_type, g1_type)
    order = np.argsort(g_all)
    g_all = g_all[order]
    g_type_all = g_type_all[order]

    sums = np.cumsum(g_type_all)

    # Where the cumulative sum is zero, we close the GTI
    closing_bins = sums == 0
    # The next element in the sequence is the start of the new GTI. In the case
    # of the last element, the next is the first. Numpy.roll gives this for
    # free.
    starting_bins = np.roll(closing_bins, 1)

    starting_times = g_all[starting_bins]
    closing_times = g_all[closing_bins]

    final_gti = []
    for start, stop in zip(starting_times, closing_times):
        final_gti.append([start, stop])

    return np.sort(final_gti, axis=0)


def time_intervals_from_gtis(gtis, chunk_length, fraction_step=1,
                             epsilon=1e-5):
    """Compute start/stop times of equal time intervals, compatible with GTIs.

    Used to start each FFT/PDS/cospectrum from the start of a GTI,
    and stop before the next gap in data (end of GTI).

    Parameters
    ----------
    gtis : 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    chunk_length : float
        Length of the time segments

    fraction_step : float
        If the step is not a full ``chunk_length`` but less (e.g. a moving window),
        this indicates the ratio between step step and ``chunk_length`` (e.g.
        0.5 means that the window shifts of half ``chunk_length``)

    Returns
    -------
    spectrum_start_times : array-like
        List of starting times to use in the spectral calculations.

    spectrum_stop_times : array-like
        List of end times to use in the spectral calculations.

    """
    spectrum_start_times = np.array([], dtype=np.longdouble)
    for g in gtis:
        if g[1] - g[0] + epsilon < chunk_length:
            continue

        newtimes = np.arange(g[0], g[1] - chunk_length + epsilon,
                             np.longdouble(chunk_length) * fraction_step,
                             dtype=np.longdouble)
        spectrum_start_times = \
            np.append(spectrum_start_times,
                      newtimes)

    assert len(spectrum_start_times) > 0, \
        ("No GTIs are equal to or longer than chunk_length.")
    return spectrum_start_times, spectrum_start_times + chunk_length


def bin_intervals_from_gtis(gtis, chunk_length, time, dt=None, fraction_step=1,
                            epsilon=0.001):
    """Compute start/stop times of equal time intervals, compatible with GTIs, and map them
    to the indices of an array of time stamps.

    Used to start each FFT/PDS/cospectrum from the start of a GTI,
    and stop before the next gap in data (end of GTI).
    In this case, it is necessary to specify the time array containing the
    times of the light curve bins.
    Returns start and stop bins of the intervals to use for the PDS

    Parameters
    ----------
    gtis : 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    chunk_length : float
        Length of each time segment

    time : array-like
        Array of time stamps

    Other Parameters
    ----------------
    dt : float, default median(diff(time))
        Time resolution of the light curve.

    epsilon : float, default 0.001
        The tolerance, in fraction of ``dt``, for the comparisons at the borders

    fraction_step : float
        If the step is not a full ``chunk_length`` but less (e.g. a moving window),
        this indicates the ratio between step step and ``chunk_length`` (e.g.
        ``0.5`` means that the window shifts of half ``chunk_length``)

    Returns
    -------
    spectrum_start_bins : array-like
        List of starting bins in the original time array to use in spectral
        calculations.

    spectrum_stop_bins : array-like
        List of end bins to use in the spectral calculations.

    Examples
    --------
    >>> time = np.arange(0.5, 13.5)

    >>> gtis = [[0, 5], [6, 8]]

    >>> chunk_length = 2

    >>> start_bins, stop_bins = bin_intervals_from_gtis(gtis,chunk_length,time)

    >>> np.all(start_bins == [0, 2, 6])
    True
    >>> np.all(stop_bins == [2, 4, 8])
    True
    >>> np.all(time[start_bins[0]:stop_bins[0]] == [0.5, 1.5])
    True
    >>> np.all(time[start_bins[1]:stop_bins[1]] == [2.5, 3.5])
    True
    """
    if dt is None:
        dt = np.median(np.diff(time))
    nbin = np.long(chunk_length / dt)

    if time[-1] < np.min(gtis) or time[0] > np.max(gtis):
        raise ValueError("Invalid time interval for the given GTIs")

    spectrum_start_bins = np.array([], dtype=np.long)
    for g in gtis:
        if g[1] - g[0] + epsilon * dt < chunk_length:
            continue
        good_low = time - dt / 2 >= g[0] - epsilon * dt
        good_up = time + dt / 2 <= g[1] + epsilon * dt
        good = good_low & good_up
        t_good = time[good]
        if len(t_good) == 0:
            continue
        startbin = np.argmin(np.abs(time - dt / 2 - g[0]))
        stopbin = np.searchsorted(time + dt / 2, g[1], 'right') + 1
        if stopbin > len(time):
            stopbin = len(time)

        if time[startbin] < g[0] + dt / 2 - epsilon * dt:
            startbin += 1
        # Would be g[1] - dt/2, but stopbin is the end of an interval
        # so one has to add one bin
        if time[stopbin - 1] > g[1] - dt / 2 + epsilon * dt:
            stopbin -= 1

        newbins = np.arange(startbin, stopbin - nbin + 1,
                            int(nbin * fraction_step), dtype=np.long)
        spectrum_start_bins = \
            np.append(spectrum_start_bins,
                      newbins)
    assert len(spectrum_start_bins) > 0, \
        ("No GTIs are equal to or longer than chunk_length.")
    return spectrum_start_bins, spectrum_start_bins + nbin


def gti_border_bins(gtis, time, dt=None, epsilon=0.001):
    """Find the indices in a time array corresponding to the borders of GTIs.

    GTIs shorter than the bin time are not returned.

    Parameters
    ----------
    gtis : 2-d float array
        List of GTIs of the form ``[[gti0_0, gti0_1], [gti1_0, gti1_1], ...]``

    time : array-like
        Time stamps of light curve bins

    Returns
    -------
    spectrum_start_bins : array-like
        List of starting bins of each GTI

    spectrum_stop_bins : array-like
        List of stop bins of each GTI. The elements corresponding to these bins
        should *not* be included.

    Examples
    --------
    >>> times = np.arange(0.5, 13.5)

    >>> start_bins, stop_bins = gti_border_bins(
    ...    [[0, 5], [6, 8]], times)

    >>> np.all(start_bins == [0, 6])
    True
    >>> np.all(stop_bins == [5, 8])
    True
    >>> np.all(times[start_bins[0]:stop_bins[0]] == [ 0.5, 1.5, 2.5, 3.5, 4.5])
    True
    >>> np.all(times[start_bins[1]:stop_bins[1]] == [6.5, 7.5])
    True
    """
    if dt is None:
        dt = np.median(np.diff(time))

    spectrum_start_bins = np.array([], dtype=np.long)
    spectrum_stop_bins = np.array([], dtype=np.long)
    for g in gtis:
        good = (time - dt / 2 >= g[0]) & (time + dt / 2 <= g[1])
        t_good = time[good]
        if len(t_good) == 0:
            continue
        startbin = np.argmin(np.abs(time - dt / 2 - g[0]))
        stopbin = np.searchsorted(time + dt / 2, g[1], 'right') + 1
        if stopbin > len(time):
            stopbin = len(time)

        if time[startbin] < g[0] + dt / 2 - epsilon * dt:
            startbin += 1
        # Would be g[1] - dt/2, but stopbin is the end of an interval
        # so one has to add one bin
        if time[stopbin - 1] > g[1] - dt / 2 + epsilon * dt:
            stopbin -= 1
        spectrum_start_bins = \
            np.append(spectrum_start_bins,
                      [startbin])
        spectrum_stop_bins = \
            np.append(spectrum_stop_bins,
                      [stopbin])
    assert len(spectrum_start_bins) > 0, \
        ("No GTIs are equal to or longer than chunk_length.")
    return spectrum_start_bins, spectrum_stop_bins
