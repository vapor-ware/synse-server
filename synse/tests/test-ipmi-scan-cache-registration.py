#!/usr/bin/env python
""" Test suite for Synse IPMI device registration

    Author: Erick Daniszewski
    Date:   01/31/2017

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
import sys
import unittest

from ipmi_scan_cache_registration.test_ipmi_scan_cache_registration import \
    IPMIScanCacheRegistrationTestCase
from vapor_common.test_utils import exit_suite, run_suite


def get_suite():
    """ Create an instance of the test suite for ipmi scan cache registration tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMIScanCacheRegistrationTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-scan-cache-registration', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
