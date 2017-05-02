#!/usr/bin/env python
""" OpenDCRE Southbound IPMI tests with device init scan disabled.

    Author: Erick Daniszewski
    Date:   10/26/2016

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http


class IPMINoInitScanTestCase(unittest.TestCase):
    """ Test that setting the "scan_on_init" flag in the OpenDCRE config
    does indeed prevent the device from performing a scan when the device
    is initialized.
    """

    def test_001_test_scan(self):
        """ Test the OpenDCRE scan endpoint. Since the BMCs were not scanned
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
