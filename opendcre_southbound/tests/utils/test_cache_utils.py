#!/usr/bin/env python
""" Tests for OpenDCRE utils' cache helpers.

    Author: Erick Daniszewski
    Date:   19 April 2017

    \\//
     \/apor IO
"""
import unittest
import opendcre_southbound.utils as utils


class CacheUtilsTestCase(unittest.TestCase):

    init_app = None

    @classmethod
    def setUpClass(cls):
        cls.init_app = utils.current_app

    @classmethod
    def tearDownClass(cls):
        utils.current_app = cls.init_app

    def test_000_get_scan_cache(self):
        """
        """
        pass

    def test_000_write_scan_cache(self):
        """
        """
        pass
