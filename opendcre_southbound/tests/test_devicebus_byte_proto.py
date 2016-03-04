#!/usr/bin/env python
"""
OpenDCRE Southbound API Devicebus Board Id and Device Id byte protocol tests
Author:  erick
Date:    11/16/2015
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
import devicebus


class ByteProtocolTestCase(unittest.TestCase):
    def test_001_board_id_to_bytes(self):
        """ Test converting a board_id to bytes.
        """
        board_id = 0xf1e2d3c4
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = 0x1
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x1])

        board_id = 0x00000000
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = 0xffffffff
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = 0x123
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

    def test_002_board_id_to_bytes(self):
        """ Test converting a board_id long to bytes.
        """
        board_id = long(0x00)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = long(0x01)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x01])

        board_id = long(0x12345678)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x12, 0x34, 0x56, 0x78])

        board_id = long(0xffff)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xff, 0xff])

        board_id = long(0xfabfab)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0xfa, 0xbf, 0xab])

        board_id = long(0x8d231a66)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x8d, 0x23, 0x1a, 0x66])

    def test_003_board_id_to_bytes(self):
        """ Test converting a board_id string to bytes.
        """
        board_id = '{0:08x}'.format(0xf1e2d3c4)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = '{0:08x}'.format(0xffffffff)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = '{0:08x}'.format(0x00000000)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = '{0:08x}'.format(0xbeef)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xbe, 0xef])

        board_id = '{0:04x}'.format(0x123)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

        board_id = '{0:02x}'.format(0x42)
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x42])

    def test_004_board_id_to_bytes(self):
        """ Test converting a board_id unicode to bytes.
        """
        board_id = unicode('{0:08x}'.format(0xf1e2d3c4))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = unicode('{0:08x}'.format(0xffffffff))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = unicode('{0:08x}'.format(0x00000000))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = unicode('{0:08x}'.format(0xbeef))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xbe, 0xef])

        board_id = unicode('{0:04x}'.format(0x123))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

        board_id = unicode('{0:02x}'.format(0x42))
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x42])

    def test_005_board_id_to_bytes(self):
        """ Test converting a board_id list to bytes.
        """
        board_id = [0x01, 0x02, 0x03, 0x04]
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

        board_id = [0xff, 0xff, 0xff, 0xff]
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

        board_id = [0x00, 0x00, 0x00, 0x00]
        board_id_bytes = devicebus.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

    def test_006_board_id_to_bytes(self):
        """ Test converting a board_id invalid type to bytes.
        """
        board_id = [0x01, 0x02, 0x03]
        with self.assertRaises(TypeError):
            devicebus.board_id_to_bytes(board_id)

        board_id = (0x01, 0x02, 0x03, 0x04)
        with self.assertRaises(TypeError):
            devicebus.board_id_to_bytes(board_id)

        board_id = float(0xf)
        with self.assertRaises(TypeError):
            devicebus.board_id_to_bytes(board_id)

        board_id = {0x01, 0x02, 0x03, 0x04}
        with self.assertRaises(TypeError):
            devicebus.board_id_to_bytes(board_id)

    def test_007_board_id_join_bytes(self):
        """ Test converting a list of board_id bytes into its original value.
        """
        board_id_bytes = [0x00, 0x00, 0x00, 0x00]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x00000000)

        board_id_bytes = [0xff, 0xff, 0xff, 0xff]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xffffffff)

        board_id_bytes = [0x00, 0x00, 0x43, 0x21]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x4321)

        board_id_bytes = [0x00, 0x00, 0x00, 0x01]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x1)

        board_id_bytes = [0xa7, 0x2b, 0x11, 0x0e]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xa72b110e)

        board_id_bytes = [0xbe, 0xef, 0x00, 0x00]
        board_id = devicebus.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xbeef0000)

    def test_008_board_id_join_bytes(self):
        """ Test converting a list of board_id bytes into its original value.
        """
        board_id_bytes = []
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

        board_id_bytes = [0x12, 0x34, 0x56]
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

        board_id_bytes = [0x12, 0x34, 0x56, 0x78, 0x90]
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

        board_id_bytes = 0x12345678
        with self.assertRaises(ValueError):
            devicebus.board_id_join_bytes(board_id_bytes)

    def test_009_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = 0xf1e2
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = 0x1
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x1])

        device_id = 0x0000
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = 0xffff
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = 0x123
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x01, 0x23])

    def test_010_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = long(0x00)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = long(0x0f)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x0f])

        device_id = long(0xffff)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = long(0xa1b)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0x1b])

        device_id = long(0xbeef)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xbe, 0xef])

    def test_011_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = '{0:04x}'.format(0xf1e2)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = '{0:04x}'.format(0x0)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = '{0:04x}'.format(0xffff)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = '{0:04x}'.format(0xabc)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0xbc])

        device_id = '{0:02x}'.format(0x12)
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x12])

    def test_012_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = unicode('{0:04x}'.format(0xf1e2))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = unicode('{0:04x}'.format(0x0))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = unicode('{0:04x}'.format(0xffff))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = unicode('{0:04x}'.format(0xabc))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0xbc])

        device_id = unicode('{0:02x}'.format(0x12))
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x12])

    def test_013_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = [0x00, 0x00]
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

        device_id = [0xff, 0xff]
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

        device_id = [0x12, 0x34]
        device_id_bytes = devicebus.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

    def test_014_device_id_join_bytes(self):
        """ Test converting a list of device_id bytes into its original value.
        """
        device_id_bytes = [0x00, 0x00]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x0000)

        device_id_bytes = [0xff, 0xff]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xffff)

        device_id_bytes = [0x43, 0x21]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x4321)

        device_id_bytes = [0x00, 0x01]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x1)

        device_id_bytes = [0xa7, 0x2b]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xa72b)

        device_id_bytes = [0xef, 0x00]
        device_id = devicebus.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xef00)

    def test_015_device_id_join_bytes(self):
        """ Test converting a list of device_id bytes into its original value.
        """
        device_id_bytes = []
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

        device_id_bytes = [0x12]
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

        device_id_bytes = [0x12, 0x34, 0x56]
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)

        device_id_bytes = 0x1234
        with self.assertRaises(ValueError):
            devicebus.device_id_join_bytes(device_id_bytes)
