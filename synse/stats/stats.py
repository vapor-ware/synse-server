#!/usr/bin/env python
""" Statistical functions used by Synse.

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import math
import sys

logger = logging.getLogger(__name__)


def std_dev(numbers):
    """ Find the average and standard deviation in numbers.

    Args:
        numbers (list[int | float]): a list of numbers.

    Returns:
        tuple[int, int]: the average and the standard deviation for
            the given list of numbers.
    """
    average = sum(numbers)/len(numbers)

    x = 0
    for raw in numbers:
        x += (raw - average) ** 2
    _std_dev = x / len(numbers)
    return average, _std_dev


def grubbs(l):
    """ Find an outlier in list l if any. We need this since the differential
    pressure sensor readings vary wildly.

    Args:
        l (list[int | float]): the list of numbers to find an outlier in.

    Returns:
        tuple[int, int]: the numbers with the max and min deviation in the list
    """
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
    """ Remove the biggest outlier from a list count number of times.

    Args:
        l (list[int | float]): list of numbers
        count (int): the number of times to remove the biggest outlier.

    Returns:
        dict: a dictionary of the stats results.
    """
    logger.debug('remove_outliers(l, count): {}, {}'.format(l, count))
    outliers = []
    result = {}

    for _ in range(count):
        _max, _ = grubbs(l)

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
    """ Remove a percentage of the list, considering them outliers.

    Args:
        l (list[int | float]): a list of numbers.
        percent (int | float): 0-1, where 0 removes none and 1 removes all.

    Returns:
        dict: a dictionary of stats so we can see what we're doing.
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
