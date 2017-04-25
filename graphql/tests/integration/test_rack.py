""" Tests for the rack schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

from nose.plugins.attrib import attr  # noqa

from ..util import BaseSchemaTest


class TestRack(BaseSchemaTest):

    def get_racks(self, query):
        return self.run_query(query).data.get("clusters")[0]["racks"]

    def test_query(self):
        keys = [
            "id",
            "is_leader",
            "is_shadow",
            "vec_ip",
            "failed_servers",
            "server_count"
        ]
        self.assertItemsEqual(self.get_racks("test_racks")[0].keys(), keys)

    def test_id_arg(self):
        self.assertEqual(len(self.get_racks("test_rack_id")), 1)
