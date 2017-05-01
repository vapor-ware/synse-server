#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Server Factory.

    \\//
     \/apor IO
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
                Rittal-RiZone
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
