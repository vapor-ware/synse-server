#!/usr/bin/env python
"""
OpenDCRE Chassis Location conversion tests
Author:  andrew
Date:    2/23/2016
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
import unittest
from location import *


class ChassisLocationTestCase(unittest.TestCase):
    def test_001_microserver_ids(self):
        device_id = (1 << IS_MICRO_BIT)
        for i in range(0x00, 0x1F):
            self.assertEqual(False, has_location(device_id+(i << 8)))
            self.assertEqual(i, get_microserver_id(device_id+(i << 8)))

    def test_002_verify_location(self):
        # these are very primitive, just a quick verification that the location function converts right
        FRONT_DEVICE = 1 << DEPTH_F_BIT
        REAR_DEVICE = 1 << DEPTH_R_BIT
        DEPTH_MID_DEVICE = FRONT_DEVICE | REAR_DEVICE
        LEFT_DEVICE = 1 << HORIZ_L_BIT
        RIGHT_DEVICE = 1 << HORIZ_R_BIT
        HORIZ_MID_DEVICE = LEFT_DEVICE | RIGHT_DEVICE
        TOP_DEVICE = 1 << VERT_T_BIT
        BOTTOM_DEVICE = 1 << VERT_B_BIT
        VERT_MID_DEVICE = TOP_DEVICE | BOTTOM_DEVICE

        # test various combinations
        self.assertEqual('middle', get_chassis_location(DEPTH_MID_DEVICE)['depth'])
        self.assertEqual('front', get_chassis_location(FRONT_DEVICE)['depth'])
        self.assertEqual('rear', get_chassis_location(REAR_DEVICE)['depth'])

        self.assertEqual('middle', get_chassis_location(HORIZ_MID_DEVICE)['horiz_pos'])
        self.assertEqual('left', get_chassis_location(LEFT_DEVICE)['horiz_pos'])
        self.assertEqual('right', get_chassis_location(RIGHT_DEVICE)['horiz_pos'])

        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE)['vert_pos'])
        self.assertEqual('top', get_chassis_location(TOP_DEVICE)['vert_pos'])
        self.assertEqual('bottom', get_chassis_location(BOTTOM_DEVICE)['vert_pos'])

        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE | HORIZ_MID_DEVICE | DEPTH_MID_DEVICE)['vert_pos'])
        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE | HORIZ_MID_DEVICE | DEPTH_MID_DEVICE)['horiz_pos'])
        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE | HORIZ_MID_DEVICE | DEPTH_MID_DEVICE)['depth'])

        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE | DEPTH_MID_DEVICE)['vert_pos'])
        self.assertEqual('unknown', get_chassis_location(VERT_MID_DEVICE | DEPTH_MID_DEVICE)['horiz_pos'])
        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE | DEPTH_MID_DEVICE)['depth'])

        self.assertEqual('middle', get_chassis_location(VERT_MID_DEVICE | LEFT_DEVICE)['vert_pos'])
        self.assertEqual('left', get_chassis_location(VERT_MID_DEVICE | LEFT_DEVICE)['horiz_pos'])
        self.assertEqual('unknown', get_chassis_location(VERT_MID_DEVICE | LEFT_DEVICE)['depth'])

        for i in range(0, 0xFF):
            self.assertDictEqual({'depth': 'unknown', 'horiz_pos': 'unknown', 'vert_pos': 'unknown', 'server_node': 'unknown'}, get_chassis_location(i))
