#!/usr/bin/env python
""" OpenDCRE Southbound Redfish Endpoint Tests

    Author: Morgan Morley Mills, based off IPMI tests by Erick Daniszewski
    Date:   02/06/2017

    \\//
     \/apor IO
"""

import unittest

from opendcre_southbound.version import __api_version__
from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
# from vapor_common.errors import VaporHTTPError


class RedfishVersionTestCase(unittest.TestCase):
    """ Test version reads with the Redfish emulator running
    """
    def test_01_version(self):
        """ Hit the OpenDCRE versionless version endpoint to verify it is
        running the correct API version.
        """
        # remove the last 4 chars (the api version) from the prefix as this endpoint
        # is version-less.
        r = http.get(PREFIX[:-4] + '/version')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['version'], __api_version__)

    def test_02_version(self):
        """ Hit the OpenDCRE versionless version endpoint to verify it is
        running the correct API version.
        """
        # remove the last 4 chars (the api version) from the prefix as this endpoint
        # is version-less.
        r = http.post(PREFIX[:-4] + '/version')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['version'], __api_version__)