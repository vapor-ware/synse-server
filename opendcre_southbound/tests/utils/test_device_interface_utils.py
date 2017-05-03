#!/usr/bin/env python
""" Tests for OpenDCRE utils' device interface helpers.

    Author: Erick Daniszewski
    Date:   19 April 2017

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
