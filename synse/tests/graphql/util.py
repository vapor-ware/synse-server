""" Utils to help out with testing

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

import json
import logging
import os

import testtools

from synse import schema

QUERY_PREVIEW_LENGTH = 1000


class BaseSchemaTest(testtools.TestCase):

    def setUp(self):
        super(BaseSchemaTest, self).setUp()
        self.schema = schema.create()

    def get_query(self, name):
        path = os.path.normpath(os.path.join(
            os.path.dirname(__file__), 'queries', '{0}.graphql'.format(name)))
        with open(path, 'r') as fobj:
            return fobj.read()

    def output(self, result):
        print(json.dumps(result.data, indent=4)[:QUERY_PREVIEW_LENGTH])

    def assertQuery(self, result):
        if result.errors is None:
            result.errors = []

        for error in result.errors:
            logging.exception('Query error', exc_info=error)
            if hasattr(error, 'message'):
                logging.debug(error.message)

        self.assertFalse(result.errors)
        self.output(result)

    def run_query(self, name):
        result = self.schema.execute(self.get_query(name))
        self.assertQuery(result)
        return result
