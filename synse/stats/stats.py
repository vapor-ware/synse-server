#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Statistical functions used by synse. This will end up getting moved out
        of synse to the embedded code.
"""

import math
import logging
import sys

logger = logging.getLogger(__name__)


def std_dev(numbers):
    """Find the average and standard deviation in numbers.
    :param numbers: A list of numbers.
    :returns: The average and the standard deviation for the numbers."""
    average = sum(numbers)/len(numbers)

    x = 0
    for raw in numbers:
        x += (raw - average) ** 2
    _std_dev = x / len(numbers)
    return average, _std_dev


def grubbs(l):
    """Find an outlier in list l if any. We need this since the differential
    pressure sensor readings vary wildly.
    :param l: The list of numbers to find an outlier in.
    :returns: The numbers with the max and min deviation in the list."""
    # See https://en.wikipedia.org/wiki/Grubbs%27_test_for_outliers

    # Find the mean and standard deviation.
    mean, stddev = std_dev(l)

    if stddev == 0:
        return None, None  # Avoid div 0.

    # Find the largest and smallest standard deviation in the list.
    max_deviation = 0
    max_deviation_number = None
    min_deviation = sys.maxsize
    min_deviation_number = None
    for x in l:
        deviation = math.fabs(x - mean) / stddev
        if deviation > max_deviation:
            max_deviation = deviation
            max_deviation_number = x
        if deviation < min_deviation:
            min_deviation = deviation
            min_deviation_number = x

    return max_deviation_number, min_deviation_number


def remove_outliers(l, count):
    """Remove the biggest outlier from a list count number of times.
    :param l: List of numbers.
    :param count: How many times to remove the biggest outlier.
    :returns: A dict with stats so that we can see what we're doing."""
    logger.debug('remove_outliers(l, count): {}, {}'.format(l, count))
    outliers = []
    result = {}

    for x in range(count):
        _max, _min = grubbs(l)

        if _max is None:
            break  # for. Note that this will remove less than count. That's okay.

        outliers.append(_max)
        l.remove(_max)

    mean, stddev = std_dev(l)

    result['removed'] = count
    result['outliers'] = outliers
    result['list'] = l
    result['mean'] = mean
    result['stddev'] = stddev
    return result


def remove_outliers_percent(l, percent):
    """Remove a percentage of the list, considering them outliers.
    :param l: List of numbers.
    :param percent: 0-1 where 0 removes none, 1 removes all.
    :returns: A dict with stats so that we can see what we're doing.
    result['removed'] is the number of items removed.
    result['outliers'] is the data that are considered outliers.
    result['list'] is the list after removing outliers.
    result['mean'] is the mean of result['list']
    result['std_dev'] is the standard deviation of result['list']
    """
    # In the future it may be better to do this until the standard deviation
    # drops below a value. The code here is what was initially tested in
    # Phoenix for leveling out the differential pressure readings for auto_fan.
    # It was clear that naive averaging was insufficient due to turbulence and
    # a wildly varying mean.
    count = int(len(l) * percent)
    return remove_outliers(l, count)
