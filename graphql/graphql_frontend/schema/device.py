""" Device schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import functools

import graphene

from . import util


def resolve_fields(cls):
    for field in cls._resolve_fields:
        setattr(
            cls,
            "resolve_{0}".format(field),
            functools.partialmethod(cls._request_data, field))
    return cls


def setup_resolve(cls):
    for field, field_cls in cls._fields:
        setattr(
            cls,
            "resolve_{0}".format(field),
            functools.partialmethod(resolve_class, field, field_cls)
        )
    return cls


def resolve_class(self, field, cls, *args, **kwargs):
    return cls(**self._data.get(field))


class ChassisLocation(graphene.ObjectType):
    depth = graphene.String(required=True)
    horiz_pos = graphene.String(required=True)
    server_node = graphene.String(required=True)
    vert_pos = graphene.String(required=True)


class PhysicalLocation(graphene.ObjectType):
    depth = graphene.String(required=True)
    horizontal = graphene.String(required=True)
    vertical = graphene.String(required=True)


@setup_resolve
class Location(graphene.ObjectType):
    _data = None
    _fields = [
        ("chassis_location", ChassisLocation),
        ("physical_location", PhysicalLocation)
    ]

    chassis_location = graphene.Field(ChassisLocation, required=True)
    physical_location = graphene.Field(PhysicalLocation, required=True)


class BoardInfo(graphene.ObjectType):
    manufacturer = graphene.String(required=True)
    part_number = graphene.String(required=True)
    product_name = graphene.String()
    serial_number = graphene.String(required=True)


class ChassisInfo(graphene.ObjectType):
    chassis_type = graphene.String(required=True)
    part_number = graphene.String(required=True)
    serial_number = graphene.String(required=True)


class ProductInfo(graphene.ObjectType):
    asset_tag = graphene.String()
    manufacturer = graphene.String()
    part_number = graphene.String()
    product_name = graphene.String()
    serial_number = graphene.String(required=True)
    version = graphene.String()


@setup_resolve
class Asset(graphene.ObjectType):
    _data = None
    _fields = [
        ("board_info", BoardInfo),
        ("chassis_info", ChassisInfo),
        ("product_info", ProductInfo)
    ]

    board_info = graphene.Field(BoardInfo, required=True)
    chassis_info = graphene.Field(ChassisInfo, required=True)
    product_info = graphene.Field(ProductInfo, required=True)


class DeviceInterface(graphene.Interface):
    _data = None

    id = graphene.String(required=True)
    device_type = graphene.String(required=True)
    info = graphene.String(required=True)
    location = graphene.Field(Location, required=True)
    asset = graphene.Field(Asset, required=True)

    @graphene.resolve_only_args
    def resolve_location(self):
        return Location(_data=self._location())

    @graphene.resolve_only_args
    def resolve_asset(self):
        return Asset(_data=self._asset())


class DeviceBase(graphene.ObjectType):
    _data = None
    _parent = None
    _root = None

    @classmethod
    def build(cls, parent, data):
        return globals().get(cls.__name__)(
            id=data.get("device_id"),
            device_type=data.get("device_type"),
            info=data.get("device_info", ""),
            _parent=parent,
            _data=data
        )

    @property
    def rack_id(self):
        return self._parent._parent.id

    @property
    def board_id(self):
        return self._parent.id

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        root = self._root
        if root is None:
            root = "read/{0}".format(self.device_type)

        return util.make_request("{0}/{1}/{2}/{3}".format(
            root,
            self.rack_id,
            self.board_id,
            self.id))

    @functools.lru_cache(maxsize=1)
    def _location(self):
        return util.make_request("location/{0}/{1}/{2}".format(
            self.rack_id,
            self.board_id,
            self.id))

    def _request_data(self, field, args, context, info):
        return self._resolve_detail().get(field)

    @functools.lru_cache(maxsize=1)
    def _asset(self):
        return util.make_request("asset/{0}/{1}/{2}".format(
            self.rack_id,
            self.board_id,
            self.id))


class SensorDevice(DeviceBase):
    class Meta:
        interfaces = (DeviceInterface, )


@resolve_fields
class TemperatureDevice(DeviceBase):
    _resolve_fields = [
        "temperature_c"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    temperature_c = graphene.Float(required=True)


@resolve_fields
class FanSpeedDevice(DeviceBase):
    _resolve_fields = [
        "health",
        "states",
        "speed_rpm"
    ]
    _root = "fan"

    class Meta:
        interfaces = (DeviceInterface, )

    health = graphene.String(required=True)
    states = graphene.List(graphene.String, required=True)
    speed_rpm = graphene.Int(required=True)


@resolve_fields
class PowerDevice(DeviceBase):
    _resolve_fields = [
        "input_power",
        "over_current",
        "power_ok",
        "power_status",
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    input_power = graphene.Float(required=True)
    over_current = graphene.Boolean(required=True)
    power_ok = graphene.Boolean(required=True)
    power_status = graphene.String(required=True)

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        return util.make_request("power/{0}/{1}/{2}/status".format(
            self.rack_id,
            self.board_id,
            self.id))


@resolve_fields
class LedDevice(DeviceBase):
    _resolve_fields = [
        "led_state"
    ]
    _root = "led"

    class Meta:
        interfaces = (DeviceInterface, )

    led_state = graphene.String(required=True)


class SystemDevice(DeviceBase):
    class Meta:
        interfaces = (DeviceInterface, )

    hostnames = graphene.List(graphene.String, required=True)
    ip_addresses = graphene.List(graphene.String, required=True)
    asset = graphene.Field(Asset, required=True)

    @graphene.resolve_only_args
    def resolve_hostnames(self):
        return self._parent._data.get("hostnames")

    @graphene.resolve_only_args
    def resolve_ip_addresses(self):
        return self._parent._data.get("ip_addresses")
