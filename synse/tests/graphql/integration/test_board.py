""" Tests for the board schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

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

from nose.plugins.attrib import attr  # noqa

from ..util import BaseSchemaTest


class TestBoard(BaseSchemaTest):

    def get_boards(self, query):
        return self.run_query(query).data.get('racks')[0].get('boards')

    def test_query(self):
        keys = ['id']
        self.assertItemsEqual(self.get_boards('test_boards')[0].keys(), keys)

    def test_id_arg(self):
        self.assertEqual(len(self.get_boards('test_board_id')), 1)
