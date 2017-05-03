#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Server Factory.

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

from ..snmp.test_device1.test_device1 import TestDevice1

logger = logging.getLogger(__name__)


class SnmpServerFactory(object):
    """Factory class for initializing specific SNMP server implementations.
    When we support a new SNMP server, add the server_type string in the
    json config file and call the constructor here.
    """

    # Map of server_type configuration strings to well known SNMP server
    # implementation class constructors. This is where the server_type gets added.
    _CONFIG_TO_CONSTRUCTOR_MAP = {
        'OpenDCRE-testDevice1': TestDevice1
    }

    @staticmethod
    def initialize_snmp_server(server_type, app_cfg, kwargs):
        """Initialize SNMP server specific class that handles OpenDCRE calls.
        :param server_type: server_type string from the json config (snmp_config.json by default.
            Supported server_types:
                Emulator-Test
                OpenDCRE-testDevice1
        :param app_cfg: The OpenDCRE app config.
        :param kwargs: kwargs from the json config.
        """
        constructor = SnmpServerFactory._CONFIG_TO_CONSTRUCTOR_MAP.get(server_type, None)
        if constructor is None:
            logger.error('Unknown SNMP server type {}.'.format(server_type))
            # This isn't throwing to avoid taking down OpenDCRE. The unknown
            # device will get registered, but won't do anything.
            # TODO: Core Ticket 590. Should throw. Should notify. Should not register.
            # Should be caught gracefully at the device registration level
            # and should not take down OpenDCRE.
            return None
        return constructor(app_cfg=app_cfg, kwargs=kwargs)
