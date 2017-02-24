#!/usr/bin/env python
""" Configuration data for the OpenDCRE Southbound test cases.

    Author:  Erick Daniszewski
    Date:    9/9/2015

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
from version import __api_version__
from opendcre_southbound import constants as const

_PORT = const.port
_ENDPOINTPREFIX = const.endpoint_prefix

PROTOCOL = 'http://'

# southbound endpoint prefix for test containers
PREFIX = PROTOCOL + 'opendcre-southbound-test-container:' + str(_PORT) + _ENDPOINTPREFIX + __api_version__

# path to the directory holding data for tests. assumes root at /vapor-core
TEST_DATA_DIR = '/opendcre/opendcre_southbound/tests/data/'
