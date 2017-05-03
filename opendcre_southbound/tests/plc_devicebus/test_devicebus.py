#!/usr/bin/env python
""" VaporCORE Southbound Devicebus Tests

    Author:  Erick Daniszewski
    Date:    10/20/2015

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
import unittest

from opendcre_southbound.devicebus.devices.plc.plc_bus import DeviceBusPacket
from opendcre_southbound.errors import BusDataException
from opendcre_southbound.utils import (
    board_id_to_bytes,
    board_id_join_bytes,
    device_id_to_bytes,
    device_id_join_bytes
)


class DevicebusTestCase(unittest.TestCase):
    """ Test the Vapor CORE devicebus
    """
    def test_001_instantiate_valid_devicebus_packet_method_A(self):
        """ Test instantiating a devicebus packet using fields as provided by the user,
        which is this case are the default values
        """
        dbp = DeviceBusPacket()
        self.assertEqual(dbp.sequence, 0x01)
        self.assertEqual(dbp.device_type, 0xFF)
        self.assertEqual(dbp.board_id, 0x00000000)
        self.assertEqual(dbp.device_id, 0xFFFF)
        self.assertEqual(dbp.data, [None])

    def test_002_instantiate_valid_devicebus_packet_method_A(self):
        """ Test initializing a devicebus packet using fields as provided by the user,
        which in this case are a mix between specified and default
        """
        dbp = DeviceBusPacket(device_type=0x01, board_id=0x00000001, device_id=0x02FF)
        self.assertEqual(dbp.sequence, 0x01)
        self.assertEqual(dbp.device_type, 0x01)
        self.assertEqual(dbp.board_id, 0x00000001)
        self.assertEqual(dbp.device_id, 0x02FF)
        self.assertEqual(dbp.data, [None])

    def test_003_instantiate_valid_devicebus_packet_method_A(self):
        """ Test initializing a devicebus packet using fields as provided by the user,
        which in this case are all specified
        """
        dbp = DeviceBusPacket(
            sequence=0x03,
            device_type=0x40,
            board_id=0x12345678,
            device_id=0xAA05,
            data=[0x1, 0x2, 0x3]
        )

        self.assertEqual(dbp.sequence, 0x03)
        self.assertEqual(dbp.device_type, 0x40)
        self.assertEqual(dbp.board_id, 0x12345678)
        self.assertEqual(dbp.device_id, 0xAA05)
        self.assertEqual(dbp.data, [0x1, 0x2, 0x3])

    def test_004_instantiate_valid_devicebus_packet_method_A(self):
        """ Test initializing a devicebus packet
        """
        dbp = DeviceBusPacket(
            sequence=0x00,
            device_type=0xFF,
            board_id=0xFF000000,
            device_id=0x0CFF,
            data=[0x1, 0x2, 0x3]
        )

        self.assertEqual(dbp.sequence, 0x00)
        self.assertEqual(dbp.device_type, 0xFF)
        self.assertEqual(dbp.board_id, 0xFF000000)
        self.assertEqual(dbp.device_id, 0x0CFF)
        self.assertEqual(dbp.data, [0x1, 0x2, 0x3])

    def test_005_instantiate_valid_devicebus_packet_method_B(self):
        """ Test instantiating a devicebus packet using the individual fields of the
        packet itself
        """
        packet = [0x01, 0x0C, 0x03, 0x40, 0x12, 0x34, 0x56, 0x78, 0xAA, 0x05, 0x1, 0x2, 0x3, 0xf4, 0x04]
        dbp = DeviceBusPacket(data_bytes=packet)
        
        self.assertEqual(dbp.sequence, 0x03)
        self.assertEqual(dbp.device_type, 0x40)
        self.assertEqual(dbp.board_id, 0x12345678)
        self.assertEqual(dbp.device_id, 0xAA05)
        self.assertEqual(dbp.data, [0x1, 0x2, 0x3])

    @unittest.skip('was a TODO -- need to implement test(s) using serial reader')
    def test_006_instantiate_valid_devicebus_packet_method_C(self):
        """ Test initializing a devicebus packet using a serial reader
        """
        pass

    def test_007_valid_devicebus_packet_serialize(self):
        """ Test serializing a packet based on constructor args
        """
        dbp = DeviceBusPacket(
            sequence=0x03,
            device_type=0x40,
            board_id=0x12345678,
            device_id=0xAA05,
            data=[0x1, 0x2, 0x3]
        )

        packet = dbp.serialize()
        expected_packet = [0x01, 0x0C, 0x03, 0x40, 0x12, 0x34, 0x56, 0x78, 0xAA, 0x05, 0x1, 0x2, 0x3, 0xf4, 0x04]
        self.assertEqual(packet, expected_packet)

    def test_008_valid_devicebus_packet_deserialize(self):
        """ Test deserializing a packet
        """
        dbp = DeviceBusPacket()

        # use a known packet
        packet = [1, 12, 3, 64, 18, 52, 86, 120, 170, 5, 1, 2, 3, 244, 4]
        dbp.deserialize(packet)

        self.assertEqual(dbp.sequence, 0x03)
        self.assertEqual(dbp.device_type, 0x40)
        self.assertEqual(dbp.board_id, 0x12345678)
        self.assertEqual(dbp.device_id, 0xAA05)
        self.assertEqual(dbp.data, [0x1, 0x2, 0x3])

    def test_009_invalid_devicebus_packet_deserialize(self):
        """ Test deserializing a packet when the length of the packet is less than
        the minimum packet length
        """
        dbp = DeviceBusPacket()

        # invalid packet
        packet = [1, 12, 3, 64, 18, 52, 86, 120, 170, 244, 4]
        with self.assertRaises(BusDataException):
            dbp.deserialize(packet)

    def test_010_invalid_devicesbus_packet_deserialize(self):
        """ Test deserializing a packet with an invalid header byte
        """
        dbp = DeviceBusPacket()

        # invalid packet
        packet = [0x00, 0x0C, 0x03, 0x40, 0x12, 0x34, 0x56, 0x78, 0xAA, 0x05, 0x1, 0x2, 0x3, 0xf4, 0x04]
        with self.assertRaises(BusDataException):
            dbp.deserialize(packet)

    def test_011_invalid_devicebus_packet_deserialize(self):
        """ Test deserializing a packet whose length byte doesnt match the length of
        the packet
        """
        dbp = DeviceBusPacket()

        # invalid packet
        packet = [0x00, 0x0B, 0x03, 0x40, 0x12, 0x34, 0x56, 0x78, 0xAA, 0x05, 0x1, 0x2, 0x3, 0xf4, 0x04]
        with self.assertRaises(BusDataException):
            dbp.deserialize(packet)

    def test_012_invalid_devicebus_packet_deserialize(self):
        """ Test deserializing a packet when the packet checksum doesnt match the
        generated checksum
        """
        dbp = DeviceBusPacket()

        # invalid packet
        packet = [0x00, 0x0B, 0x03, 0x40, 0x12, 0x34, 0x56, 0x78, 0xAA, 0x05, 0x1, 0x2, 0x3, 0xf0, 0x04]
        with self.assertRaises(BusDataException):
            dbp.deserialize(packet)

    def test_013_invalid_devicebus_packet_deserialize(self):
        """ Test deserializing a packet where the trailer byte is invalid
        """
        dbp = DeviceBusPacket()

        # invalid packet
        packet = [0x00, 0x0B, 0x03, 0x40, 0x12, 0x34, 0x56, 0x78, 0xAA, 0x05, 0x1, 0x2, 0x3, 0xf4, 0x03]
        with self.assertRaises(BusDataException):
            dbp.deserialize(packet)

    def test_014_test_board_id_byte_conversion_01(self):
        """ Test converting a board_id value to its byte array value, then back
        to the board_id value
        """
        board_id = 0x28c5ad11

        bid_bytes = board_id_to_bytes(board_id)
        self.assertEqual(bid_bytes, [0x28, 0xc5, 0xad, 0x11])

        new_board_id = board_id_join_bytes(bid_bytes)
        self.assertEqual(new_board_id, board_id)

    def test_015_test_board_id_byte_conversion_02(self):
        """ Test converting a board_id value to its byte array value, then back
        to the board_id value
        """
        board_id = 0x00000000

        bid_bytes = board_id_to_bytes(board_id)
        self.assertEqual(bid_bytes, [0x00, 0x00, 0x00, 0x00])

        new_board_id = board_id_join_bytes(bid_bytes)
        self.assertEqual(new_board_id, board_id)

    def test_016_test_board_id_byte_conversion_03(self):
        """ Test converting a board_id value to its byte array value, then back
        to the board_id value
        """
        board_id = 0xFFFFFFFF

        bid_bytes = board_id_to_bytes(board_id)
        self.assertEqual(bid_bytes, [0xFF, 0xFF, 0xFF, 0xFF])

        new_board_id = board_id_join_bytes(bid_bytes)
        self.assertEqual(new_board_id, board_id)

    def test_017_test_device_id_byte_conversion_01(self):
        """ Test converting a device_id value to its byte array value, then back
        to the device_id value
        """
        device_id = 0xFFFF

        did_bytes = device_id_to_bytes(device_id)
        self.assertEqual(did_bytes, [0xFF, 0xFF])

        new_device_id = device_id_join_bytes(did_bytes)
        self.assertEqual(new_device_id, device_id)

    def test_018_test_device_id_byte_conversion_02(self):
        """ Test converting a device_id value to its byte array value, then back
        to the device_id value
        """
        device_id = 0x0000

        did_bytes = device_id_to_bytes(device_id)
        self.assertEqual(did_bytes, [0x00, 0x00])

        new_device_id = device_id_join_bytes(did_bytes)
        self.assertEqual(new_device_id, device_id)

    def test_019_test_device_id_byte_conversion_03(self):
        """ Test converting a device_id value to its byte array value, then back
        to the device_id value
        """
        device_id = 0x01c4

        did_bytes = device_id_to_bytes(device_id)
        self.assertEqual(did_bytes, [0x01, 0xc4])

        new_device_id = device_id_join_bytes(did_bytes)
        self.assertEqual(new_device_id, device_id)

    def test_020_test_serialize_deserialize(self):
        """ Test serializing and deserializing a DeviceBusPacket
        """
        dbp = DeviceBusPacket(
            sequence=0x00,
            device_type=0xFF,
            board_id=0xFF000000,
            device_id=0x0CFF,
            data=[0x1, 0x2, 0x3]
        )

        packet = dbp.serialize()

        # 0 everything out so we know deserialization actually did something
        dbp.sequence = 0
        dbp.device_type = 0
        dbp.board_id = 0
        dbp.device_id = 0
        dbp.data = [0]

        dbp.deserialize(packet)

        self.assertEqual(dbp.sequence, 0x00)
        self.assertEqual(dbp.device_type, 0xFF)
        self.assertEqual(dbp.board_id, 0xFF000000)
        self.assertEqual(dbp.device_id, 0x0CFF)
        self.assertEqual(dbp.data, [0x1, 0x2, 0x3])

    def test_021_test_serialize_deserialize(self):
        """ Test serializing and deserializing a DeviceBusPacket
        """
        dbp = DeviceBusPacket(
            sequence=0x03,
            device_type=0x40,
            board_id=0x12345678,
            device_id=0xAA05,
            data=[0x1, 0x2, 0x3]
        )

        packet = dbp.serialize()

        # 0 everything out so we know deserialization actually did something
        dbp.sequence = 0
        dbp.device_type = 0
        dbp.board_id = 0
        dbp.device_id = 0
        dbp.data = [0]

        dbp.deserialize(packet)

        self.assertEqual(dbp.sequence, 0x03)
        self.assertEqual(dbp.device_type, 0x40)
        self.assertEqual(dbp.board_id, 0x12345678)
        self.assertEqual(dbp.device_id, 0xAA05)
        self.assertEqual(dbp.data, [0x1, 0x2, 0x3])

    def test_022_test_serialize_deserialize(self):
        """ Test serializing and deserializing a DeviceBusPacket
        """
        dbp = DeviceBusPacket(
            sequence=0xFF,
            device_type=0xFF,
            board_id=0xFFFFFFFF,
            device_id=0xFFFF,
            data=[0xFF, 0xFF, 0xFF]
        )

        packet = dbp.serialize()

        # 0 everything out so we know deserialization actually did something
        dbp.sequence = 0
        dbp.device_type = 0
        dbp.board_id = 0
        dbp.device_id = 0
        dbp.data = [0]

        dbp.deserialize(packet)

        self.assertEqual(dbp.sequence, 0xFF)
        self.assertEqual(dbp.device_type, 0xFF)
        self.assertEqual(dbp.board_id, 0xFFFFFFFF)
        self.assertEqual(dbp.device_id, 0xFFFF)
        self.assertEqual(dbp.data, [0xFF, 0xFF, 0xFF])

    def test_023_test_serialize_deserialize(self):
        """ Test serializing and deserializing a DeviceBusPacket
        """
        dbp = DeviceBusPacket(
            sequence=0x00,
            device_type=0x00,
            board_id=0x00000000,
            device_id=0x0000,
            data=[0x0, 0x0, 0x0]
        )

        packet = dbp.serialize()

        # F everything out so we know deserialization actually did something
        dbp.sequence = 0xFF
        dbp.device_type = 0xFF
        dbp.board_id = 0xFFFFFFFF
        dbp.device_id = 0xFFFF
        dbp.data = [0xFF, 0xFF]

        dbp.deserialize(packet)

        self.assertEqual(dbp.sequence, 0x00)
        self.assertEqual(dbp.device_type, 0x00)
        self.assertEqual(dbp.board_id, 0x00000000)
        self.assertEqual(dbp.device_id, 0x0000)
        self.assertEqual(dbp.data, [0x0, 0x0, 0x0])

    def test_024_test_serialize_deserialize(self):
        """ Test serializing and deserializing a DeviceBusPacket
        """
        dbp = DeviceBusPacket(
            sequence=0xA0,
            device_type=0xB3,
            board_id=0xFA00B3E9,
            device_id=0xF011,
            data=[0x1B, 0xAA, 0xF0]
        )

        packet = dbp.serialize()

        # 0 everything out so we know deserialization actually did something
        dbp.sequence = 0
        dbp.device_type = 0
        dbp.board_id = 0
        dbp.device_id = 0
        dbp.data = [0]

        dbp.deserialize(packet)

        self.assertEqual(dbp.sequence, 0xA0)
        self.assertEqual(dbp.device_type, 0xB3)
        self.assertEqual(dbp.board_id, 0xFA00B3E9)
        self.assertEqual(dbp.device_id, 0xF011)
        self.assertEqual(dbp.data, [0x1B, 0xAA, 0xF0])
