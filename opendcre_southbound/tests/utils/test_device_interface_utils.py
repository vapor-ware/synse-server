#!/usr/bin/env python
""" Tests for OpenDCRE utils' device interface helpers.

    Author: Erick Daniszewski
    Date:   19 April 2017

    \\//
     \/apor IO
"""
import unittest
import opendcre_southbound.utils as utils


class DeviceInterfaceUtilsTestCase(unittest.TestCase):
    
    init_app = None

    @classmethod
    def setUpClass(cls):
        cls.init_app = utils.current_app

    @classmethod
    def tearDownClass(cls):
        utils.current_app = cls.init_app

    def test_000_get_device_instance(self):
        """
        """
        pass
