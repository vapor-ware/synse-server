#!/usr/bin/env python
""" Tests for OpenDCRE utils' validation/noramlization helpers.

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


class ValidationUtilsTestCase(unittest.TestCase):

    def test_000_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        board_id, device_id = utils.check_valid_board_and_device('0', '0')
        self.assertEqual(board_id, 0x00)
        self.assertEqual(device_id, 0x00)

    def test_001_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        board_id, device_id = utils.check_valid_board_and_device('abc', '123')
        self.assertEqual(board_id, 0xabc)
        self.assertEqual(device_id, 0x123)

    def test_002_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        board_id, device_id = utils.check_valid_board_and_device('ffffffff', 'ffff')
        self.assertEqual(board_id, 0xffffffff)
        self.assertEqual(device_id, 0xffff)

    def test_003_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        with self.assertRaises(ValueError):
            utils.check_valid_board_and_device('ffffffffff', 'ffff')

    def test_004_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        with self.assertRaises(ValueError):
            utils.check_valid_board_and_device('0', 'ffffffffff')

    def test_005_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        with self.assertRaises(ValueError):
            utils.check_valid_board_and_device('-1', '0')

    def test_006_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        with self.assertRaises(ValueError):
            utils.check_valid_board_and_device('0', '-1')

    def test_007_check_valid_board_and_device(self):
        """ Test validating that board and device ids are correct.
        """
        board_id, device_id = utils.check_valid_board_and_device('board', 'device')
        self.assertEqual(board_id, 'board')
        self.assertEqual(device_id, 'device')

    def test_000_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        board_id = utils.check_valid_board('0')
        self.assertEqual(board_id, 0x00)

    def test_001_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        board_id = utils.check_valid_board('0abc')
        self.assertEqual(board_id, 0xabc)

    def test_002_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        board_id = utils.check_valid_board('ffffffff')
        self.assertEqual(board_id, 0xffffffff)

    def test_003_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        with self.assertRaises(ValueError):
            utils.check_valid_board('ffffffffffffff')

    def test_004_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        with self.assertRaises(ValueError):
            utils.check_valid_board('-1')

    def test_005_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        board_id = utils.check_valid_board('not a hex string')
        self.assertEqual(board_id, 'not a hex string')

    def test_006_check_valid_board(self):
        """ Test validating that board ids are correct.
        """
        board_id = utils.check_valid_board('10.1.10.1')
        self.assertEqual(board_id, '10.1.10.1')
