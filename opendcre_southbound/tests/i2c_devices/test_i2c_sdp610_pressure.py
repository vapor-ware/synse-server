#!/usr/bin/env python
""" OpenDCRE Southbound I2C Endpoint Tests

    Author: Andrew Cencini
    Date:   10/19/2016

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.devicebus.devices.i2c.sdp610_pressure import SDP610Pressure


class SDP610TestCase(unittest.TestCase):
    """ Test case for I2C SDP610 Pressure device.
    """

    def test_000_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test within the bounds of the correction factor steps.
        """
        corr = SDP610Pressure._altitude_correction(10)
        self.assertEqual(corr, 0.95)

        corr = SDP610Pressure._altitude_correction(260)
        self.assertEqual(corr, 0.98)

        corr = SDP610Pressure._altitude_correction(435)
        self.assertEqual(corr, 1.00)

        corr = SDP610Pressure._altitude_correction(510)
        self.assertEqual(corr, 1.01)

        corr = SDP610Pressure._altitude_correction(760)
        self.assertEqual(corr, 1.04)

        corr = SDP610Pressure._altitude_correction(1510)
        self.assertEqual(corr, 1.15)

        corr = SDP610Pressure._altitude_correction(2260)
        self.assertEqual(corr, 1.26)

        corr = SDP610Pressure._altitude_correction(3010)
        self.assertEqual(corr, 1.38)

    def test_001_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test on the lower bounds of the correction factor steps.
        """
        corr = SDP610Pressure._altitude_correction(0)
        self.assertEqual(corr, 0.95)

        corr = SDP610Pressure._altitude_correction(250)
        self.assertEqual(corr, 0.98)

        corr = SDP610Pressure._altitude_correction(425)
        self.assertEqual(corr, 1.00)

        corr = SDP610Pressure._altitude_correction(500)
        self.assertEqual(corr, 1.01)

        corr = SDP610Pressure._altitude_correction(750)
        self.assertEqual(corr, 1.04)

        corr = SDP610Pressure._altitude_correction(1500)
        self.assertEqual(corr, 1.15)

        corr = SDP610Pressure._altitude_correction(2250)
        self.assertEqual(corr, 1.26)

        corr = SDP610Pressure._altitude_correction(3000)
        self.assertEqual(corr, 1.38)

    def test_002_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test on the upper bounds of the correction factor steps.
        """
        corr = SDP610Pressure._altitude_correction(249)
        self.assertEqual(corr, 0.95)

        corr = SDP610Pressure._altitude_correction(424)
        self.assertEqual(corr, 0.98)

        corr = SDP610Pressure._altitude_correction(499)
        self.assertEqual(corr, 1.00)

        corr = SDP610Pressure._altitude_correction(749)
        self.assertEqual(corr, 1.01)

        corr = SDP610Pressure._altitude_correction(1499)
        self.assertEqual(corr, 1.04)

        corr = SDP610Pressure._altitude_correction(2249)
        self.assertEqual(corr, 1.15)

        corr = SDP610Pressure._altitude_correction(2999)
        self.assertEqual(corr, 1.26)

        corr = SDP610Pressure._altitude_correction(1000000000)  # no upper bound here, so just large int
        self.assertEqual(corr, 1.38)

    def test_003_altitude_correction(self):
        """ Test the altitude correction factor method.

        Here, we test on the upper bounds of the correction factor steps. In this
        case, we pass in a float.
        """
        corr = SDP610Pressure._altitude_correction(249.99)
        self.assertEqual(corr, 0.95)

        corr = SDP610Pressure._altitude_correction(424.99)
        self.assertEqual(corr, 0.98)

        corr = SDP610Pressure._altitude_correction(499.99)
        self.assertEqual(corr, 1.00)

        corr = SDP610Pressure._altitude_correction(749.99)
        self.assertEqual(corr, 1.01)

        corr = SDP610Pressure._altitude_correction(1499.99)
        self.assertEqual(corr, 1.04)

        corr = SDP610Pressure._altitude_correction(2249.99)
        self.assertEqual(corr, 1.15)

        corr = SDP610Pressure._altitude_correction(2999.99)
        self.assertEqual(corr, 1.26)

        corr = SDP610Pressure._altitude_correction(1000000000.99)  # no upper bound here, so just large int
        self.assertEqual(corr, 1.38)

    def test_004_altitude_correction(self):
        """ Test the altitude correction factor method.

        Test passing in a value lower than 0 (below sea level).
        """
        with self.assertRaises(ValueError):
            SDP610Pressure._altitude_correction(-1)

    def test_005_altitude_correction(self):
        """ Test the altitude correction factor method.

        Test passing in a value much lower than 0 (below sea level).
        """
        with self.assertRaises(ValueError):
            SDP610Pressure._altitude_correction(-9999999)

    def test_006_altitude_correction(self):
        """ Test the altitude correction factor method.

        Test passing in a value lower than 0 (below sea level). In this case,
        the value is a float.
        """
        with self.assertRaises(ValueError):
            SDP610Pressure._altitude_correction(-5.99)
