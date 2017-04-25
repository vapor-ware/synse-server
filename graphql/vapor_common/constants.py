#!/usr/bin/env python
""" Common definitions used across Vapor components.

    Author: Andrew Cencini
    Date:   06/24/2016

    \\//
     \/apor IO
"""

LICENSE_PATH = '/etc/vapor/cert'

LOCAL_HASH = 'local_hash'

# the container volume in auto-discovery which will be used to serve
# an unblock state to any containers attached to that volume.
BOOTSTRAP_STATE_VOLUME = '/vapor/state'

MAX_VAPOR_FAN_SPEED_RPM = 2000
MIN_VAPOR_FAN_SPEED_RPM = 0

CLUSTER_ID = 'ClusterID'
RACK_ID = 'RackID'
BOARD_ID = 'BoardID'
DEVICE_ID = 'DeviceID'

PLC_RACK_ID = 'vapor_plc_rack'
