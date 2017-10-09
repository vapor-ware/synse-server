#!/usr/bin/env python
""" Synse I2C Endpoint Tests

    Author: Andrew Cencini
    Date:   10/19/2016

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

import unittest
from collections import Counter

from synse.protocols.conversions import conversions
from synse.stats import stats


class SDP610TestCase(unittest.TestCase):
    """ Test case for I2C SDP610 Pressure device.
    """

    def test_000_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test within the bounds of the correction factor steps.
        """
        corr = conversions.differential_pressure_sdp610_altitude(10)
        self.assertEqual(corr, 0.95)

        corr = conversions.differential_pressure_sdp610_altitude(260)
        self.assertEqual(corr, 0.98)

        corr = conversions.differential_pressure_sdp610_altitude(435)
        self.assertEqual(corr, 1.00)

        corr = conversions.differential_pressure_sdp610_altitude(510)
        self.assertEqual(corr, 1.01)

        corr = conversions.differential_pressure_sdp610_altitude(760)
        self.assertEqual(corr, 1.04)

        corr = conversions.differential_pressure_sdp610_altitude(1510)
        self.assertEqual(corr, 1.15)

        corr = conversions.differential_pressure_sdp610_altitude(2260)
        self.assertEqual(corr, 1.26)

        corr = conversions.differential_pressure_sdp610_altitude(3010)
        self.assertEqual(corr, 1.38)

    def test_001_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test on the lower bounds of the correction factor steps.
        """
        corr = conversions.differential_pressure_sdp610_altitude(0)
        self.assertEqual(corr, 0.95)

        corr = conversions.differential_pressure_sdp610_altitude(250)
        self.assertEqual(corr, 0.98)

        corr = conversions.differential_pressure_sdp610_altitude(425)
        self.assertEqual(corr, 1.00)

        corr = conversions.differential_pressure_sdp610_altitude(500)
        self.assertEqual(corr, 1.01)

        corr = conversions.differential_pressure_sdp610_altitude(750)
        self.assertEqual(corr, 1.04)

        corr = conversions.differential_pressure_sdp610_altitude(1500)
        self.assertEqual(corr, 1.15)

        corr = conversions.differential_pressure_sdp610_altitude(2250)
        self.assertEqual(corr, 1.26)

        corr = conversions.differential_pressure_sdp610_altitude(3000)
        self.assertEqual(corr, 1.38)

    def test_002_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test on the upper bounds of the correction factor steps.
        """
        corr = conversions.differential_pressure_sdp610_altitude(249)
        self.assertEqual(corr, 0.95)

        corr = conversions.differential_pressure_sdp610_altitude(424)
        self.assertEqual(corr, 0.98)

        corr = conversions.differential_pressure_sdp610_altitude(499)
        self.assertEqual(corr, 1.00)

        corr = conversions.differential_pressure_sdp610_altitude(749)
        self.assertEqual(corr, 1.01)

        corr = conversions.differential_pressure_sdp610_altitude(1499)
        self.assertEqual(corr, 1.04)

        corr = conversions.differential_pressure_sdp610_altitude(2249)
        self.assertEqual(corr, 1.15)

        corr = conversions.differential_pressure_sdp610_altitude(2999)
        self.assertEqual(corr, 1.26)

        corr = conversions.differential_pressure_sdp610_altitude(1000000000)  # no upper bound here, so just large int
        self.assertEqual(corr, 1.38)

    def test_003_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test on the upper bounds of the correction factor steps. In this
        case, we pass in a float.
        """
        corr = conversions.differential_pressure_sdp610_altitude(249.99)
        self.assertEqual(corr, 0.95)

        corr = conversions.differential_pressure_sdp610_altitude(424.99)
        self.assertEqual(corr, 0.98)

        corr = conversions.differential_pressure_sdp610_altitude(499.99)
        self.assertEqual(corr, 1.00)

        corr = conversions.differential_pressure_sdp610_altitude(749.99)
        self.assertEqual(corr, 1.01)

        corr = conversions.differential_pressure_sdp610_altitude(1499.99)
        self.assertEqual(corr, 1.04)

        corr = conversions.differential_pressure_sdp610_altitude(2249.99)
        self.assertEqual(corr, 1.15)

        corr = conversions.differential_pressure_sdp610_altitude(2999.99)
        self.assertEqual(corr, 1.26)

        # No upper bound here, so just large int.
        corr = conversions.differential_pressure_sdp610_altitude(1000000000.99)
        self.assertEqual(corr, 1.38)

    def test_004_altitude_correction(self):
        """ Test the altitude correction factor method.

        Test passing in a value lower than 0 (below sea level).
        """
        corr = conversions.differential_pressure_sdp610_altitude(-1)
        self.assertEqual(corr, 0.95)

    def test_005_altitude_correction(self):
        """ Test the altitude correction factor method.

        Test passing in a value much lower than 0 (below sea level).
        """
        corr = conversions.differential_pressure_sdp610_altitude(-9999999)
        self.assertEqual(corr, 0.95)

    def test_006_altitude_correction(self):
        """ Test the altitude correction factor method.

        Test passing in a value lower than 0 (below sea level). In this case,
        the value is a float.
        """
        corr = conversions.differential_pressure_sdp610_altitude(-5.99)
        self.assertEqual(corr, 0.95)

    def test_007_stats(self):
        """Test the stats corrections for the differential pressure reads."""
        readings = [-668.8, -668.8, -479.75, -593.75, -398.04999999999995,
                    -593.75, -720.1, -501.59999999999997, -694.4499999999999,
                    -398.04999999999995, -694.4499999999999, -668.8, -288.8,
                    -904.4, -116.85, -720.1, -525.35, -546.25, -619.4, -668.8,
                    -720.1, -501.59999999999997, -668.8, -323.95,
                    -872.0999999999999]
        result = stats.remove_outliers_percent(readings, .3)

        # Verify all fields.
        self.assertIn('list', result)
        self.assertIn('removed', result)
        self.assertIn('stddev', result)
        self.assertIn('outliers', result)
        self.assertIn('mean', result)

        # Verify data
        expected = [-668.8, -668.8, -479.75, -593.75, -593.75, -720.1,
                    -501.59999999999997, -694.4499999999999,
                    -694.4499999999999, -668.8, -720.1, -525.35, -546.25,
                    -619.4, -668.8, -720.1, -501.59999999999997, -668.8]
        self.assertTrue(Counter(expected) == Counter(result['list']),
                        msg='result[list]: {}'.format(
                            result['list']))

        self.assertEquals(7, result['removed'])
        self.assertTrue(6446.5 < result['stddev'] < 6446.6,
                        msg='result[stddev]: {}'.format(
                            result['stddev']))

        expected = [-116.85, -288.8, -323.95, -904.4, -872.0999999999999,
                    -398.04999999999995, -398.04999999999995]
        self.assertTrue(Counter(expected) == Counter(result['outliers']),
                        msg='result[outliers]: {}'.format(
                            result['outliers']))

        self.assertTrue(-625.3 < result['mean'] < -625.2,
                        msg='result[mean]: {}'.format(
                            result['mean']))
