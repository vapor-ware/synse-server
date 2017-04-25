""" Board Schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import graphene
import inflection

from . import device, util


class Board(graphene.ObjectType):
    _data = None
    _parent = None

    id = graphene.String(required=True)
    devices = graphene.List(
        device.DeviceInterface,
        required=True,
        device_type=graphene.String()
    )

    @staticmethod
    def build(parent, data):
        return Board(id=data.get("board_id"), _data=data, _parent=parent)

    def device_class(self, device_type):
        return getattr(
            device,
            "{0}Device".format(inflection.camelize(device_type)),
            device.SensorDevice)

    @graphene.resolve_only_args
    def resolve_devices(self, device_type=None):
        return [self.device_class(d.get("device_type")).build(self, d)
                for d in util.arg_filter(
                    device_type,
                    lambda x: x.get("device_type") == device_type,
                    self._data.get("devices"))]
