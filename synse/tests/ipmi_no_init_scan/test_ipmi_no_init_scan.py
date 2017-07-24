#!/usr/bin/env python
""" Synse IPMI tests with device init scan disabled.

    Author: Erick Daniszewski
    Date:   10/26/2016

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

from synse.tests.test_config import PREFIX
from synse.vapor_common import http


class IPMINoInitScanTestCase(unittest.TestCase):
    """ Test that setting the "scan_on_init" flag in the Synse config
    does indeed prevent the device from performing a scan when the device
    is initialized.
    """

    def test_001_test_scan(self):
        """ Test the Synse scan endpoint. Since the BMCs were not scanned
        on init, we expect that there should be no boards found for the two
        racks specified in the bmc_config file.
        """
        r = http.get(PREFIX + '/scan', timeout=30)
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 2)

        for rack in racks:
            self.assertIsInstance(rack, dict)
            self.assertIn('rack_id', rack)
            self.assertIn('boards', rack)

            self.assertIn(rack['rack_id'], ['rack_1', 'rack_2'])
            self.assertEqual(rack['boards'], [])
