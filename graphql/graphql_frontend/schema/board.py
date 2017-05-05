""" Board schema

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
        return Board(id=data.get('board_id'), _data=data, _parent=parent)

    @staticmethod
    def device_class(device_type):
        return getattr(
            device,
            '{0}Device'.format(inflection.camelize(device_type)),
            device.SensorDevice)

    @graphene.resolve_only_args
    def resolve_devices(self, device_type=None):
        return [self.device_class(d.get('device_type')).build(self, d)
                for d in util.arg_filter(
                    device_type,
                    lambda x: x.get('device_type') == device_type,
                    self._data.get('devices'))]
