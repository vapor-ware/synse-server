#!/usr/bin/env python
""" Tests for OpenDCRE utils' board id helpers.

    Author: Erick Daniszewski
    Date:   19 April 2017

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
import opendcre_southbound.utils as utils


class BoardIdUtilsTestCase(unittest.TestCase):

    def test_000_normalize_board_id(self):
        """ Test normalizing the board id to a string.
        """
        normalized = utils.normalize_board_id(0x00000000)
        self.assertEqual(normalized, '00000000')

    def test_001_normalize_board_id(self):
        """ Test normalizing the board id to a string.
        """
        normalized = utils.normalize_board_id(0x0)
        self.assertEqual(normalized, '00000000')

    def test_002_normalize_board_id(self):
        """ Test normalizing the board id to a string.
        """
        normalized = utils.normalize_board_id(0xffffffff)
        self.assertEqual(normalized, 'ffffffff')

    def test_003_normalize_board_id(self):
        """ Test normalizing the board id to a string.
        """
        normalized = utils.normalize_board_id(0x123a)
        self.assertEqual(normalized, '0000123a')

    def test_004_normalize_board_id(self):
        """ Test normalizing the board id to a string.
        """
        normalized = utils.normalize_board_id('10.1.10.1')
        self.assertEqual(normalized, '10.1.10.1')

    def test_005_normalize_board_id(self):
        """ Test normalizing the board id to a string.
        """
        normalized = utils.normalize_board_id('666')
        self.assertEqual(normalized, '666')

    def test_000_board_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.board_id_to_hex_string(0x00000000)
        self.assertEqual(hex_string, '00000000')

    def test_001_board_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.board_id_to_hex_string(0x0)
        self.assertEqual(hex_string, '00000000')

    def test_002_board_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.board_id_to_hex_string(0x123)
        self.assertEqual(hex_string, '00000123')

    def test_003_board_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.board_id_to_hex_string(0xffffffff)
        self.assertEqual(hex_string, 'ffffffff')

    def test_004_board_id_to_string(self):
        """ Test converting an int to its hex string representation.

        In this case, the given int is greater than 4 bytes.
        """
        hex_string = utils.board_id_to_hex_string(0xffffffffff)
        self.assertEqual(hex_string, 'ffffffffff')

    def test_005_board_id_to_string(self):
        """ Test converting an int to its hex string representation.

        In this case, the given parameter is not an int, so the
        conversion should fail.
        """
        with self.assertRaises(ValueError):
            utils.board_id_to_hex_string('not-a-hex-int')

    def test_006_board_id_to_string(self):
        """ Test converting an int to its hex string representation.

        In this case, the given parameter is not an int (though does
        have valid hex string values) so it should fail.
        """
        with self.assertRaises(ValueError):
            utils.board_id_to_hex_string('666')

    def test_001_board_id_to_bytes(self):
        """ Test converting a board_id to bytes.
        """
        board_id = 0xf1e2d3c4
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = 0x1
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x1])

        board_id = 0x00000000
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = 0xffffffff
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = 0x123
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

    def test_002_board_id_to_bytes(self):
        """ Test converting a board_id long to bytes.
        """
        board_id = long(0x00)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = long(0x01)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x01])

        board_id = long(0x12345678)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x12, 0x34, 0x56, 0x78])

        board_id = long(0xffff)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xff, 0xff])

        board_id = long(0xfabfab)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0xfa, 0xbf, 0xab])

        board_id = long(0x8d231a66)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x8d, 0x23, 0x1a, 0x66])

    def test_003_board_id_to_bytes(self):
        """ Test converting a board_id string to bytes.
        """
        board_id = '{0:08x}'.format(0xf1e2d3c4)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = '{0:08x}'.format(0xffffffff)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = '{0:08x}'.format(0x00000000)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = '{0:08x}'.format(0xbeef)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xbe, 0xef])

        board_id = '{0:04x}'.format(0x123)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

        board_id = '{0:02x}'.format(0x42)
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x42])

    def test_004_board_id_to_bytes(self):
        """ Test converting a board_id unicode to bytes.
        """
        board_id = unicode('{0:08x}'.format(0xf1e2d3c4))
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xf1, 0xe2, 0xd3, 0xc4])

        board_id = unicode('{0:08x}'.format(0xffffffff))
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0xff, 0xff, 0xff, 0xff])

        board_id = unicode('{0:08x}'.format(0x00000000))
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x00])

        board_id = unicode('{0:08x}'.format(0xbeef))
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0xbe, 0xef])

        board_id = unicode('{0:04x}'.format(0x123))
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x01, 0x23])

        board_id = unicode('{0:02x}'.format(0x42))
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id_bytes, [0x00, 0x00, 0x00, 0x42])

    def test_005_board_id_to_bytes(self):
        """ Test converting a board_id list to bytes.
        """
        board_id = [0x01, 0x02, 0x03, 0x04]
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

        board_id = [0xff, 0xff, 0xff, 0xff]
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

        board_id = [0x00, 0x00, 0x00, 0x00]
        board_id_bytes = utils.board_id_to_bytes(board_id)
        self.assertEqual(board_id, board_id_bytes)

    def test_006_board_id_to_bytes(self):
        """ Test converting a board_id invalid type to bytes.
        """
        board_id = [0x01, 0x02, 0x03]
        with self.assertRaises(TypeError):
            utils.board_id_to_bytes(board_id)

        board_id = (0x01, 0x02, 0x03, 0x04)
        with self.assertRaises(TypeError):
            utils.board_id_to_bytes(board_id)

        board_id = float(0xf)
        with self.assertRaises(TypeError):
            utils.board_id_to_bytes(board_id)

        board_id = {0x01, 0x02, 0x03, 0x04}
        with self.assertRaises(TypeError):
            utils.board_id_to_bytes(board_id)

    def test_007_board_id_join_bytes(self):
        """ Test converting a list of board_id bytes into its original value.
        """
        board_id_bytes = [0x00, 0x00, 0x00, 0x00]
        board_id = utils.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x00000000)

        board_id_bytes = [0xff, 0xff, 0xff, 0xff]
        board_id = utils.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xffffffff)

        board_id_bytes = [0x00, 0x00, 0x43, 0x21]
        board_id = utils.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x4321)

        board_id_bytes = [0x00, 0x00, 0x00, 0x01]
        board_id = utils.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0x1)

        board_id_bytes = [0xa7, 0x2b, 0x11, 0x0e]
        board_id = utils.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xa72b110e)

        board_id_bytes = [0xbe, 0xef, 0x00, 0x00]
        board_id = utils.board_id_join_bytes(board_id_bytes)
        self.assertEquals(board_id, 0xbeef0000)

    def test_008_board_id_join_bytes(self):
        """ Test converting a list of board_id bytes into its original value.
        """
        board_id_bytes = []
        with self.assertRaises(ValueError):
            utils.board_id_join_bytes(board_id_bytes)

        board_id_bytes = [0x12, 0x34, 0x56]
        with self.assertRaises(ValueError):
            utils.board_id_join_bytes(board_id_bytes)

        board_id_bytes = [0x12, 0x34, 0x56, 0x78, 0x90]
        with self.assertRaises(ValueError):
            utils.board_id_join_bytes(board_id_bytes)

        board_id_bytes = 0x12345678
        with self.assertRaises(ValueError):
            utils.board_id_join_bytes(board_id_bytes)
