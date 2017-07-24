""" Device schema

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
# pylint: disable=old-style-class,no-init

import graphene
from pylru import lrudecorator

from . import util


def resolve_fields(cls):
    """ Class decorator to set the _resolve_fields member values
    as methods onto the class.

    Args:
        cls: the class being decorated.

    Returns:
        the class with new attributes assigned.
    """
    for field in cls._resolve_fields:
        setattr(
            cls,
            'resolve_{0}'.format(field),
            util.partialmethod(cls._request_data, field))
    return cls


def setup_resolve(cls):
    """ Class decorator to set the _fields member values as
    methods onto the class.

    Args:
        cls: the class being decorated.

    Returns:
        the class with new attributes assigned.
    """
    for field, field_cls in cls._fields:
        setattr(
            cls,
            'resolve_{0}'.format(field),
            util.partialmethod(resolve_class, field, field_cls)
        )
    return cls


def resolve_class(self, field, cls, *args, **kwargs):  # pylint: disable=unused-argument
    """ Partial method that will be used in `setup_resolve` to be
    applied to a decorated class.

    Args:
        self: reference to the decorated class.
        field: the field for which a 'resolve' method will be created.
        cls: the class associated with the given field.
        args: additional arguments.
        kwargs: additional keyword arguments.
    """
    return cls(**self._data.get(field))


class ChassisLocation(graphene.ObjectType):
    """ Model for chassis location.
    """

    depth = graphene.String(required=True)
    horiz_pos = graphene.String(required=True)
    server_node = graphene.String(required=True)
    vert_pos = graphene.String(required=True)


class PhysicalLocation(graphene.ObjectType):
    """ Model for physical location.
    """

    depth = graphene.String(required=True)
    horizontal = graphene.String(required=True)
    vertical = graphene.String(required=True)


@setup_resolve
class Location(graphene.ObjectType):
    """ Model for a complete location.
    """

    _data = None
    _fields = [
        ('chassis_location', ChassisLocation),
        ('physical_location', PhysicalLocation)
    ]

    chassis_location = graphene.Field(ChassisLocation, required=True)
    physical_location = graphene.Field(PhysicalLocation, required=True)


class BoardInfo(graphene.ObjectType):
    """ Model for board information.
    """

    manufacturer = graphene.String(required=True)
    part_number = graphene.String(required=True)
    product_name = graphene.String()
    serial_number = graphene.String(required=True)


class ChassisInfo(graphene.ObjectType):
    """ Model for chassis information.
    """

    chassis_type = graphene.String(required=True)
    part_number = graphene.String(required=True)
    serial_number = graphene.String(required=True)


class ProductInfo(graphene.ObjectType):
    """ Model for product information.
    """

    asset_tag = graphene.String()
    manufacturer = graphene.String()
    part_number = graphene.String()
    product_name = graphene.String()
    serial_number = graphene.String(required=True)
    version = graphene.String()


@setup_resolve
class Asset(graphene.ObjectType):
    """ Model for all asset information.
    """

    _data = None
    _fields = [
        ('board_info', BoardInfo),
        ('chassis_info', ChassisInfo),
        ('product_info', ProductInfo)
    ]

    board_info = graphene.Field(BoardInfo, required=True)
    chassis_info = graphene.Field(ChassisInfo, required=True)
    product_info = graphene.Field(ProductInfo, required=True)


class DeviceInterface(graphene.Interface):
    """ Interface for all devices.
    """

    _data = None

    id = graphene.String(required=True)
    device_type = graphene.String(required=True)
    info = graphene.String(required=True)
    location = graphene.Field(Location, required=True)
    asset = graphene.Field(Asset, required=True)
    timestamp = graphene.Int()
    request_received = graphene.Int()

    @graphene.resolve_only_args
    def resolve_location(self):
        """ Resolve the location of the device.
        """
        return Location(_data=self._location())

    @graphene.resolve_only_args
    def resolve_asset(self):
        """ Resolve the asset info of the device.
        """
        return Asset(_data=self._asset())

    @graphene.resolve_only_args
    def resolve_timestamp(self):
        """ Resolve the timestamp of the device request.
        """
        return self._resolve_detail().get('timestamp')

    @graphene.resolve_only_args
    def resolve_request_received(self):
        """ Resolve the request received time of the device request.
        """
        return self._resolve_detail().get('request_received')


class DeviceBase(graphene.ObjectType):
    """ Base class for all devices.
    """

    _data = None
    _parent = None
    _root = None

    @classmethod
    def build(cls, parent, data):
        """ Build a new instance of the device.

        Args:
            parent: the parent object for the device.
            data: the data associated with the device to build.

        Returns:
            a new instance of the built device.
        """
        return globals().get(cls.__name__)(
            id=data.get('device_id'),
            device_type=data.get('device_type'),
            info=data.get('device_info', ''),
            _parent=parent,
            _data=data
        )

    @property
    def rack_id(self):
        """ Get the rack id for the rack which the device resides on.
        """
        return self._parent._parent.id

    @property
    def board_id(self):
        """ Get the board id for the board which the device resides on.
        """
        return self._parent.id

    @lrudecorator(1)
    def _resolve_detail(self):
        """ Make a read request for the given device.
        """
        root = self._root
        if root is None:
            root = 'read/{0}'.format(self.device_type)

        return util.make_request('{0}/{1}/{2}/{3}'.format(
            root,
            self.rack_id,
            self.board_id,
            self.id))

    @lrudecorator(1)
    def _location(self):
        """ Make a location request for the given device.
        """
        return util.make_request('location/{0}/{1}/{2}'.format(
            self.rack_id,
            self.board_id,
            self.id))

    def _request_data(self, field, args, context, info):  # pylint: disable=unused-argument
        """ Get the specified field from a device request response.

        Args:
            field: the field to extract from the request response.
            args: unused
            context: unused
            info: unused
        """
        return self._resolve_detail().get(field)

    @lrudecorator(1)
    def _asset(self):
        """ Make an asset info request for the given device.
        """
        return util.make_request('asset/{0}/{1}/{2}'.format(
            self.rack_id,
            self.board_id,
            self.id))


class SensorDevice(DeviceBase):
    """ A general sensor device.
    """

    class Meta:
        interfaces = (DeviceInterface, )


@resolve_fields
class TemperatureDevice(DeviceBase):
    """ Model for a temperature type device.
    """

    _resolve_fields = [
        'temperature_c'
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    temperature_c = graphene.Float()


@resolve_fields
class FanSpeedDevice(DeviceBase):
    """ Model for a fan speed type device.
    """

    _resolve_fields = [
        'health',
        'states',
        'speed_rpm'
    ]
    _root = 'fan'

    class Meta:
        interfaces = (DeviceInterface, )

    health = graphene.String(required=True)
    states = graphene.List(graphene.String, required=True)
    speed_rpm = graphene.Int(required=True)


@resolve_fields
class PowerDevice(DeviceBase):
    """ Model for a power type device.
    """

    _resolve_fields = [
        'input_power',
        'over_current',
        'power_ok',
        'power_status'
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    input_power = graphene.Float(required=True)
    over_current = graphene.Boolean(required=True)
    power_ok = graphene.Boolean(required=True)
    power_status = graphene.String(required=True)

    @lrudecorator(1)
    def _resolve_detail(self):
        """ Make a power status request for the power device.
        """
        return util.make_request('power/{0}/{1}/{2}/status'.format(
            self.rack_id,
            self.board_id,
            self.id))


@resolve_fields
class LedDevice(DeviceBase):
    """ Model for an LED type device.
    """

    _resolve_fields = [
        'led_state'
    ]
    _root = 'led'

    class Meta:
        interfaces = (DeviceInterface, )

    led_state = graphene.String(required=True)


@resolve_fields
class VoltageDevice(DeviceBase):
    """ Model for a voltage type device.
    """

    _resolve_fields = [
        'voltage'
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    voltage = graphene.Float()


@resolve_fields
class PressureDevice(DeviceBase):
    """ Model for a pressure type device.
    """

    _resolve_fields = [
        'pressure_pa'
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    pressure_pa = graphene.Float(required=True)


class SystemDevice(DeviceBase):
    """ Model for a system device.
    """

    class Meta:
        interfaces = (DeviceInterface, )

    hostnames = graphene.List(graphene.String, required=True)
    ip_addresses = graphene.List(graphene.String, required=True)
    asset = graphene.Field(Asset, required=True)

    @graphene.resolve_only_args
    def resolve_hostnames(self):
        """ Get the hostnames associated with a system device.
        """
        return self._parent._data.get('hostnames')

    @graphene.resolve_only_args
    def resolve_ip_addresses(self):
        """ Get the ip addresses associated with a system device.
        """
        return self._parent._data.get('ip_addresses')

    def _resolve_detail(self):
        """ Override request resolution for system devices.

        Override here to return an empty dictionary for system devices. Since
        systems don't have a supported read action, we will forgo the request
        overhead and just return an empty dictionary to be handled upstream.
        """
        return {}
