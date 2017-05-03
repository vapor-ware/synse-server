#!/usr/bin/env python
""" OpenDCRE Byte/Bit Definitions

    Author:  Erick Daniszewski
    Date:    11/16/2015

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

# hard-code the bit within a 4-byte board id which corresponds to a given protocol
# directive, for convenience and consistency

SCAN_ALL_BIT = 31
IPMI_BIT = 30
SHUFFLE_BIT = 29
SAVE_BIT = 28

# define the 4-byte board ids which have the appropriate bits set in the upper byte
# for internal protocol directives

SCAN_ALL_BOARD_ID = 1 << SCAN_ALL_BIT  # set bit 7 of upper byte of board_id to 1=SCAN_ALL (0x80000000)
IPMI_BOARD_ID = 1 << IPMI_BIT          # set bit 6 of upper byte of board_id to 1=IPMI (0x40000000)
SHUFFLE_BOARD_ID = 1 << SHUFFLE_BIT    # set bit 5 of upper byte of board_id to 1=SHUFFLE (0x20000000)
SAVE_BOARD_ID = 1 << SAVE_BIT          # set bit 4 of upper byte of board_id to 1=SAVE (0x10000000)


# fan speed constraints
MAX_FAN_SPEED = 10000
MIN_FAN_SPEED = 0


# BMC port
BMC_PORT = 623
