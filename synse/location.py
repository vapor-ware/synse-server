#!/usr/bin/env python
""" Synse Location Support

    Author:  andrew
    Date:    2/23/2016 - Add device_id location translation.

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

IS_MICRO_BIT = 15
DEPTH_F_BIT = 14
DEPTH_R_BIT = 13
HORIZ_L_BIT = 12
HORIZ_R_BIT = 11
VERT_T_BIT = 10
VERT_B_BIT = 9


def has_location(device_id=None):
    """ Used to determine if a device_id has location information encoded in it,
    or if it refers to a microserver.

    Args:
        device_id:

    Returns:
        bool: True if device_id has location bits encoded in it, False if
            it has microserver ID bits in it.
    """
    if (device_id >> IS_MICRO_BIT) & 0x01:
        return False
    return True


def get_microserver_id(device_id=None):
    """ Get the ID of a given microserver. This is done by shifting the
    upper byte over into the lower byte, and then masking off the relevant
    bits (0..6) to get the microserver id.

    This function assumes that device_id is in fact a valid microserver (where
    IS_MICRO_BIT = 1).

    Args:
        device_id: The device_id to get microserver id for.

    Returns:
        int: The microserver ID.
    """
    return (device_id >> 8) & 0x1F


def get_chassis_location(device_id=None):
    """ Get the location of a device in a given chassis.

    This function assumes that device_id does in fact contain location bits (as
    opposed to microserver id).

    Args:
        device_id:  The device id to get location for

    Returns:
        dict: A dict containing the intra-chassis location of the device.
    """
    chassis_location = {'depth': 'unknown', 'horiz_pos': 'unknown', 'vert_pos': 'unknown', 'server_node': 'unknown'}

    if has_location(device_id):
        if (device_id >> HORIZ_L_BIT) & 0x01:
            if (device_id >> HORIZ_R_BIT) & 0x01:
                chassis_location['horiz_pos'] = 'middle'
            else:
                chassis_location['horiz_pos'] = 'left'
        elif (device_id >> HORIZ_R_BIT) & 0x01:
            chassis_location['horiz_pos'] = 'right'

        if (device_id >> DEPTH_F_BIT) & 0x01:
            if (device_id >> DEPTH_R_BIT) & 0x01:
                chassis_location['depth'] = 'middle'
            else:
                chassis_location['depth'] = 'front'
        elif (device_id >> DEPTH_R_BIT) & 0x01:
            chassis_location['depth'] = 'rear'

        if (device_id >> VERT_T_BIT) & 0x01:
            if (device_id >> VERT_B_BIT) & 0x01:
                chassis_location['vert_pos'] = 'middle'
            else:
                chassis_location['vert_pos'] = 'top'
        elif (device_id >> VERT_B_BIT) & 0x01:
            chassis_location['vert_pos'] = 'bottom'
    else:
        chassis_location['server_node'] = get_microserver_id(device_id)

    return chassis_location
