#!/usr/bin/env python
""" Configuration data for the Synse test cases.

    Author:  Erick Daniszewski
    Date:    9/9/2015

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
from synse.version import __api_version__

from synse import constants as const

_PORT = const.port
_ENDPOINTPREFIX = const.endpoint_prefix

PROTOCOL = 'http://'

# synse endpoint prefix for test containers
PREFIX = PROTOCOL + 'synse-test-container:' + str(_PORT) + _ENDPOINTPREFIX + __api_version__

# path to the directory holding data for tests. assumes root at /synse
TEST_DATA_DIR = '/synse/synse/tests/data/'

# device used by pymodbus for direct connection to emulator
RS485_TEST_CLIENT_DEVICE = '/dev/ttyVapor004'

# timeout to be used by the test client for RS485
RS485_TEST_TIMEOUT_SEC = 0.025
