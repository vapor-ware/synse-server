""" Tests for the notification schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

from nose.plugins.attrib import attr  # noqa

from ..util import BaseSchemaTest


class TestNotification(BaseSchemaTest):

    def get_notifications(self, query):
        return self.run_query(query).data.get("notifications")

    def test_query(self):
        keys = [
            "_id",
            "code",
            "resolved_on",
            "severity",
            "source",
            "status",
            "text",
            "timestamp"
        ]
        source_keys = [
            "BoardID",
            "DeviceID",
            "DeviceType",
            "Field",
            "RackID",
            "Reading",
            "ZoneID"
        ]
        notification = self.get_notifications("test_notifications")[0]
        self.assertItemsEqual(notification.keys(), keys)
        self.assertItemsEqual(notification.get("source", {}), source_keys)

    @attr("now")
    def test_id_arg(self):
        self.assertEqual(
            len(self.get_notifications("test_notification_id")), 1)
