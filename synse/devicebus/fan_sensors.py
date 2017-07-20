#!/usr/bin/env python

import datetime
import logging

from synse.devicebus.devices.i2c.max11608_adc_thermistor import \
    Max11608Thermistor
from synse.devicebus.devices.i2c.sdp610_pressure import SDP610Pressure
from synse.protocols.i2c_common import i2c_common

logger = logging.getLogger(__name__)


class FanSensor(object):
    """Simple data about a sensor. These sensors are all related to auto-fan
     and may not be on the fan controller proper. (Most are not)."""
    def __init__(self, name, units, device):
        if name is None:
            raise ValueError('name is none')
        # There could be dimensionless data, so no unit seems legal.
        if device is None:
            raise ValueError('device is none')
        self.name = name
        self.units = units
        self.device = device
        self.reading = None

    def __str__(self):
        return 'FanSensor: (name: {}, units:{}, device {}, reading {})>'.format(
            self.name, self.units, self.device, self.reading)

    def __repr__(self):
        return self.__str__()


class FanSensors(object):
    """Collection of all sensors on a single VEC read by auto-fan. This
    represents a single read of all sensors except the ones on the fan
    controller itself."""

    # Maximum number of supported thermistors.
    SUPPORTED_THERMISTOR_COUNT = 12
    # Maximum number of supported differential pressure sensors..
    SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT = 3

    def __init__(self):
        """Initialize the FanSensors object which is used for the fan_sensors
        route for auto fan."""
        # We need to differ initialization until after app_config['DEVICES'] is
        # setup (all devices are registered).
        self.initialized = False
        self.app_config = None
        self.start_time = None
        self.end_time = None
        self.read_time = None
        self.thermistors = None
        self.differentialPressures = None
        self.thermistor_read_count = None
        self.differential_pressure_read_count = None

    def initialize(self, app_config):
        """Initialize the FanSensors object which is used for the fan_sensors
        route for auto fan.
        :param app_config: Flask app.config."""

        if self.initialized:
            return

        if 'DEVICES' not in app_config:
            logger.debug('Unable to initialize FanSensors since all devices are not yet registered.')
            return  # We need to wait for all devices to register.

        self.app_config = app_config

        # Reading info
        self.start_time = None
        self.end_time = None
        self.read_time = None

        # From i2c.

        # FUTURE: All thermistors need the same device_name to support bulk reads.
        # It doesn't matter now since we're not even using device_name from the synse
        # config for production i2c sensor reads. Also true for differential pressure (i2c as well).
        thermistor_devices = self._find_devices_by_instance_name(Max11608Thermistor.get_instance_name())
        # List length FanSensors.SUPPORTED_THERMISTOR_COUNT, all entries are None.
        self.thermistors = [None] * FanSensors.SUPPORTED_THERMISTOR_COUNT
        for d in thermistor_devices:
            channel = d.channel
            self.thermistors[channel] = FanSensor('thermistor_{}'.format(channel), 'C', d)

        differential_pressure_devices = \
            self._find_devices_by_instance_name(SDP610Pressure.get_instance_name())
        # List length SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT, all entries are None.
        self.differentialPressures = [None] * FanSensors.SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT
        for d in differential_pressure_devices:
            channel = d.channel
            channel_ordinal = FanSensors._get_channel_ordinal(channel)
            self.differentialPressures[channel_ordinal] = \
                FanSensor('differential_pressure_{}'.format(channel_ordinal), 'Pa', d)

        # Compute the number of thermistors and differential pressure sensors to read.
        self.thermistor_read_count = self._thermistor_read_count()
        self.differential_pressure_read_count = self._differential_pressure_read_count()

        self._dump()

        self.initialized = True

        # TODO: Need at least minimal config checks here or elsewhere. (ticket(s))
        # https://github.com/vapor-ware/auto_fan/issues/70
        # No fan => auto-fan not supported. (check in auto-fan)
        # No temp sensors and no thermistors on all VECs => auto-fan not supported. (check here)
        # No differential pressure sensors on all VECs => auto-fan can still be supported.
        # We cannot currently support production hardware with multiple serial ports,
        #   because we don't have it, but we should prepare for that.
        # Zero or more than one humidity or airflow sensors.
        # All thermistors need the same device_name for bulk reads.
        #   We can support multiple, we just haven't done it yet and don't have the hardware.
        # All differential pressure sensors need the same device_name for bulk reads.
        #   We can support multiple, we just haven't done it yet and don't have the hardware.

    def _clear_old_readings(self):
        """Clears out previous readings for a new pass."""
        for t in self.thermistors:
            if t is not None:
                t.reading = None
        for dp in self.differentialPressures:
            if dp is not None:
                dp.reading = None

    def _differential_pressure_read_count(self):
        """Determine the number of differential pressure
        sensors to read on each _read_differential_pressures call.
        :returns: The number of differential pressure sensors to read on each
        call."""
        # Find the maximum channel for each differential pressure sensor.
        # Compute ordinal.
        max_channel = -1
        for dpressure in self.differentialPressures:
            if dpressure is not None and dpressure.device is not None:
                if dpressure.device.channel > max_channel:
                    max_channel = dpressure.device.channel

        result = FanSensors._get_channel_ordinal(max_channel)
        result += 1
        if result > FanSensors.SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT:
            raise ValueError('Unsupported differential pressure sensor count {}. Maximum {}'.format(
                result, FanSensors.SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT))
        return result

    def _dump(self):
        """Dump all fan sensors to the log so that we can see what we are
        doing."""
        logger.debug('Dumping FanSensors:')
        for t in self.thermistors:
            logger.debug('thermistor:  {}'.format(t))
        for dp in self.differentialPressures:
            logger.debug('pressure:  {}'.format(dp))
        logger.debug('thermistor read count {}'.format(self.thermistor_read_count))
        logger.debug('d pressure read count {}'.format(self.differential_pressure_read_count))

    def _find_devices_by_instance_name(self, instance_name):
        """Used on initialization to find a device by class name.
        :param instance_name: The device model to check for.
        :returns: A list of all devices of the_type."""
        logger.debug('_find_devices_by_instance_name')
        result = []
        devices = self.app_config['DEVICES']
        for d in devices.values():
            if d.__class__.get_instance_name() == instance_name:
                result.append(d)
        return result

    @staticmethod
    def _get_channel_ordinal(channel):
        """The airflow sensor has a channel setting that uses a bit shift.
        :raises: ValueError on invalid channel."""
        channels = [1, 2, 4, 8, 16, 32, 64, 128]
        return channels.index(channel)

    def _read_thermistors(self):
        readings = i2c_common.read_thermistors(self.thermistor_read_count)
        for i, reading in enumerate(readings):
            self.thermistors[i].reading = reading

    # TODO: We need to get more data out than just the reading here.
    def _read_differential_pressures(self):
        readings = i2c_common.read_differential_pressures(self.differential_pressure_read_count)
        for i, reading in enumerate(readings):
            self.differentialPressures[i].reading = reading

    def _thermistor_read_count(self):
        """Determine the number of thermistors to read on each
        _read_thermistors call.
        :returns: The number of thermistors to read on each call."""
        # Find the maximum channel for each thermistor. Add 1.
        max_channel = -1
        for thermistor in self.thermistors:
            if thermistor is not None and thermistor.device is not None:
                if thermistor.device.channel > max_channel:
                    max_channel = thermistor.device.channel
        result = max_channel + 1
        if result > FanSensors.SUPPORTED_THERMISTOR_COUNT:
            raise ValueError('Unsupported thermistor count {}. Maximum {}'.format(
                result, FanSensors.SUPPORTED_THERMISTOR_COUNT))
        return result

    def read_sensors(self):
        """Read all sensors on the local VEC. Store the readings."""
        self._clear_old_readings()
        self.start_time = datetime.datetime.now()
        self._read_thermistors()
        self._read_differential_pressures()
        self.end_time = datetime.datetime.now()
        self.read_time = (self.end_time - self.start_time).total_seconds() * 1000
