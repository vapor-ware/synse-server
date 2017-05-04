#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Device Registration Tests

    \\//
     \/apor IO
"""

import logging
import os

logger = logging.getLogger(__name__)


class Pinger(object):
    """Simple class to ping a server or container. Note: Not tested on Windows."""

    @staticmethod
    def ping(hostname):
        """Ping the host at hostname.
        :param hostname: The host to ping.
        :returns: Zero on success, nonzero on failure."""
        rc = os.system('ping -c 1 ' + hostname)
        if rc == 0:
            logger.debug('ping {} succeeded.'.format(hostname))
        else:
            logger.debug('ping {} failed with code {}.'.format(hostname, rc))
        return rc
