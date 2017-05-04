#!/usr/bin/env python
""" Common definitions used across Vapor components.

    Author: Andrew Cencini
    Date:   06/24/2016

    \\//
     \/apor IO
"""

import os

# Where any package is installed to on the container.
PACKAGE_INSTALL_DIR = '/usr/local/lib/python2.7/dist-packages/'
# Where the vapor_common package is installed on any container.
VAPOR_COMMON_PACKAGE_INSTALL_DIR = os.path.join(PACKAGE_INSTALL_DIR, 'vapor_common')

MAX_VAPOR_FAN_SPEED_RPM = 2000
MIN_VAPOR_FAN_SPEED_RPM = 0

CLUSTER_ID = 'ClusterID'
RACK_ID = 'RackID'
BOARD_ID = 'BoardID'
DEVICE_ID = 'DeviceID'

PLC_RACK_ID = 'vapor_plc_rack'
