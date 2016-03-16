#!/usr/bin/env python
"""
Configuration data for the OpenDCRE Southbound test cases.
Author:  erick
Date:    9/9/2015
    \\//
     \/apor IO

Copyright (C) 2015-16  Vapor IO

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
from vapor_common.vapor_config import ConfigManager

# get pertinent config data from the opendcre config file. assumes root at /opendcre
cfg = ConfigManager('/opendcre/opendcre_config.json')
_PORT = cfg.port
_ENDPOINTPREFIX = cfg.endpoint_prefix
_SSL_ENABLE = cfg.ssl_enable

# determine the protocol to use based on config
PROTOCOL = 'https://' if _SSL_ENABLE else 'http://'

# southbound endpoint prefix for test containers
PREFIX = PROTOCOL + 'opendcre-southbound-test-container:' + str(_PORT) + _ENDPOINTPREFIX + __api_version__

# test user/pass for http basic auth via requests lib
TEST_USERNAME = "vaporadmin"
TEST_PASSWORD = "vaporcore"

# path to the directory holding data for tests. assumes root at /opendcre
TEST_DATA_DIR = '/opendcre/opendcre_southbound/tests/data/'

# path to ssl certs configured for the opendcre-southbound-test-container
SSL_CERT = '/opendcre/opendcre_southbound/tests/test_certs/opendcre.crt'
