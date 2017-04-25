""" Device schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import functools

import graphene

from . import util
from .. import config


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


class DeviceInterface(graphene.Interface):
    _data = None

    id = graphene.String(required=True)
    device_type = graphene.String(required=True)
    info = graphene.String(required=True)
    location = graphene.Field(Location, required=True)

    def resolve_location(self, *args, **kwargs):
        return Location(_data=self._data.get("location"))


class DeviceBase(graphene.ObjectType):
    _data = None
    _parent = None

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
    def cluster_id(self):
        return self._parent._parent._parent.id

    @property
    def rack_id(self):
        return self._parent._parent.id

    @property
    def board_id(self):
        return self._parent.id

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        if config.options.get("mode") == 'opendcre':
            return util.make_request("read/{0}/{1}/{2}/{3}".format(
                self.device_type,
                self.rack_id,
                self.board_id,
                self.id))

        return util.make_request("read/{0}/{1}/{2}/{3}/{4}".format(
            self.cluster_id,
            self.rack_id,
            self.device_type,
            self.board_id,
            self.id))

    def _request_data(self, field, args, context, info):
        return self._resolve_detail().get(field)


# thomasr: since VaporBatteryDevice is a noop right now, it just uses this.
class SensorDevice(DeviceBase):
    class Meta:
        interfaces = (DeviceInterface, )


@resolve_fields
class PressureDevice(DeviceBase):
    _resolve_fields = [
        "pressure_kpa"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    pressure_kpa = graphene.String(required=True)


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
        "fan_mode",
        "speed_rpm"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    fan_mode = graphene.String(required=True)
    speed_rpm = graphene.Int(required=True)


# thomasr: another very slight difference between vapor and non vapor device.
@resolve_fields
class VaporFanDevice(DeviceBase):
    _resolve_fields = [
        "fan_mode",
        "speed_rpm"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    fan_mode = graphene.String(required=True)
    speed_rpm = graphene.Int(required=True)

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        return util.make_request("fan/{0}/{1}/{2}/{3}".format(
            self.cluster_id,
            self.rack_id,
            self.board_id,
            self.id))


@resolve_fields
class PowerDevice(DeviceBase):
    _resolve_fields = [
        "input_power",
        "input_voltage",
        "output_current",
        "over_current",
        "pmbus_raw",
        "power_ok",
        "power_status",
        "under_voltage"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    input_power = graphene.Float(required=True)
    input_voltage = graphene.Float(required=True)
    output_current = graphene.Float(required=True)
    over_current = graphene.Boolean(required=True)
    pmbus_raw = graphene.String(required=True)
    power_ok = graphene.Boolean(required=True)
    power_status = graphene.String(required=True)
    under_voltage = graphene.Boolean(required=True)

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        base = "power"
        if config.options.get("mode") == 'core':
            base += '/{0}'.format(self.cluster_id)

        data = util.make_request("{0}/{1}/{2}/{3}/status".format(
            base,
            self.rack_id,
            self.board_id,
            self.id))

        if config.options.get("mode") == 'opendcre':
            data.update({
                "input_voltage": 0.0,
                "output_current": 0.0,
                "pmbus_raw": "",
                "under_voltage": False
            })

        return data


# thomasr: this is a huge cut and paste because of something weird going on
# with inheritance and graphene. Should be fixed!
@resolve_fields
class VaporRectifierDevice(PowerDevice):
    _resolve_fields = [
        "input_power",
        "input_voltage",
        "output_current",
        "over_current",
        "pmbus_raw",
        "power_ok",
        "power_status",
        "under_voltage"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    input_power = graphene.Float(required=True)
    input_voltage = graphene.Float(required=True)
    output_current = graphene.Float(required=True)
    over_current = graphene.Boolean(required=True)
    pmbus_raw = graphene.String(required=True)
    power_ok = graphene.Boolean(required=True)
    power_status = graphene.String(required=True)
    under_voltage = graphene.Boolean(required=True)


@resolve_fields
class VaporLedDevice(DeviceBase):
    _resolve_fields = [
        "blink_state",
        "led_color",
        "led_state"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    blink_state = graphene.String(required=True)
    led_color = graphene.String(required=True)
    led_state = graphene.String(required=True)

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        return util.make_request(
            "led/{0}/{1}/{2}/{3}/no_override/no_override/no_override".format(
                self.cluster_id,
                self.rack_id,
                self.board_id,
                self.id))


# thomasr: LEDs are subtly different than vapor_leds =(
@resolve_fields
class LedDevice(DeviceBase):
    _resolve_fields = [
        "led_state"
    ]

    class Meta:
        interfaces = (DeviceInterface, )

    led_state = graphene.String(required=True)

    @functools.lru_cache(maxsize=1)
    def _resolve_detail(self):
        base = "led"
        if config.options.get("mode") == 'core':
            base += '/{0}'.format(self.cluster_id)

        return util.make_request("{0}/{1}/{2}/{3}".format(
            base,
            self.rack_id,
            self.board_id,
            self.id))


class BoardInfo(graphene.ObjectType):
    manufacturer = graphene.String(required=True)
    part_number = graphene.String(required=True)
    product_name = graphene.String(required=True)
    serial_number = graphene.String(required=True)


class ChassisInfo(graphene.ObjectType):
    chassis_type = graphene.String(required=True)
    part_number = graphene.String(required=True)
    serial_number = graphene.String(required=True)


class ProductInfo(graphene.ObjectType):
    asset_tag = graphene.String(required=True)
    manufacturer = graphene.String(required=True)
    part_number = graphene.String(required=True)
    product_name = graphene.String(required=True)
    serial_number = graphene.String(required=True)
    version = graphene.String(required=True)


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


class SystemDevice(DeviceBase):
    class Meta:
        interfaces = (DeviceInterface, )

    hostnames = graphene.List(graphene.String, required=True)
    ip_addresses = graphene.List(graphene.String, required=True)
    asset = graphene.Field(Asset, required=True)

    def resolve_hostnames(self, *args, **kwargs):
        return self._data.get("hostnames")

    def resolve_ip_addresses(self, *args, **kwargs):
        return self._data.get("ip_addresses")

    def resolve_asset(self, *args, **kwargs):
        return Asset(_data=self._data.get("asset"))
