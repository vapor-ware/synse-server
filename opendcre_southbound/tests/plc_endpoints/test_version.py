#!/usr/bin/env python
""" VaporCORE Southbound API Version Tests

    Author:  andrew
    Date:    4/13/2015
    
    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.version import __api_version__
from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError


class VersionTestCase(unittest.TestCase):
    """ Test board version issues that may arise.
    """

    def test_000_version_endpoint(self):
        """ Hit the OpenDCRE versionless version endpoint to verify it is
        running the correct API version.
        """
        # remove the last 4 chars (the api version) from the prefix as this endpoint
        # is version-less.
        r = http.get(PREFIX[:-4] + '/version')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['version'], __api_version__)

    def test_001_version_endpoint(self):
        """ Hit the OpenDCRE versionless version endpoint to verify it is
        running the correct API version.
        """
        # remove the last 4 chars (the api version) from the prefix as this endpoint
        # is version-less.
        r = http.post(PREFIX[:-4] + '/version')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['version'], __api_version__)

    def test_002_simple_version(self):
        """ Test simple version (valid board, valid version)
        """
        r = http.get(PREFIX + "/version/rack_1/0000000A")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "Version Response 1")

    def test_003_very_long_version(self):
        """ Test long version (valid board, valid version)
        Technically > 32 bytes will split stuff into multiple packets.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/0000000B")

        self.assertEqual(ctx.exception.status, 500)

    def test_004_empty_version(self):
        """ Test empty version (valid board, empty version)
        """
        r = http.get(PREFIX + "/version/rack_1/0000000C")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "")

    def test_005_many_board_versions(self):
        """ Test many board versions (valid boards, various versions)
        """
        for x in range(5):
            r = http.get(PREFIX + "/version/rack_1/" + "{0:08x}".format(x + 13))
            self.assertTrue(http.request_ok(r.status_code))
            response = r.json()
            self.assertEqual(response["firmware_version"], "Version 0x0" + str(x + 1))

    def test_006_long_data(self):
        """ Data > 32 bytes (should be multiple packets but we cheat currently)
        """
        r = http.get(PREFIX + "/version/rack_1/00000012")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")

    def test_007_bad_data(self):
        """ Bad checksum, bad trailer.
        """
        # bad trailer
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/000000B5")

        self.assertEqual(ctx.exception.status, 500)

        # bad checksum
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/000000BF")

        self.assertEqual(ctx.exception.status, 500)

    def test_008_no_data(self):
        """ Timeout.
        """
        # timeout
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/0000C800")

        self.assertEqual(ctx.exception.status, 500)

    def test_009_bad_url(self):
        """ Timeout.
        """
        # bad url
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/")

        self.assertEqual(ctx.exception.status, 404)

    def test_010_device_id_representation(self):
        """ Test version while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + "/version/rack_1/A")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = http.get(PREFIX + "/version/rack_1/00A")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = http.get(PREFIX + "/version/rack_1/00000A")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = http.get(PREFIX + "/version/rack_1/000000000A")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = http.get(PREFIX + "/version/rack_1/00000000000000000A")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "Version Response 1")

    def test_011_invalid_board_id(self):
        """ Test version while specifying invalid board_id representation.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/-1")

        self.assertEqual(ctx.exception.status, 500)
