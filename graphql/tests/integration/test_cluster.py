""" Tests for the cluster schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

from nose.plugins.attrib import attr  # noqa

from ..util import BaseSchemaTest


class TestCluster(BaseSchemaTest):

    def get_clusters(self, query):
        return self.run_query(query).data.get("clusters")

    def test_basic_query(self):
        clusters = self.get_clusters("test_cluster_basic")
        self.assertTrue(clusters)
        self.assertItemsEqual(clusters[0].keys(), ["id"])

    def test_all_fields(self):
        keys = [
            "id",
            "hardware_version",
            "leader_service_profile",
            "model_number",
            "serial_number",
            "vendor"
        ]
        cluster = self.get_clusters("test_cluster_all")[0]
        self.assertItemsEqual(cluster.keys(), keys)

    def test_args(self):
        self.assertEqual(len(self.get_clusters("test_cluster_args")), 1)
