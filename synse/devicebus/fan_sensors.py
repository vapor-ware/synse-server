#!/usr/bin/env python
""" Backend model for fan sensors and common actions around the fan
sensors.

    Author: Matt Hink
    Date:   06/15/2017

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

import datetime
import json
import logging

from synse.devicebus.devices.i2c.max116xx_adc_thermistor import Max11608Thermistor
from synse.devicebus.devices.i2c.sdp610_pressure import SDP610Pressure
from synse.protocols.i2c_common import i2c_common
from synse.vapor_common.vapor_config import ConfigManager

logger = logging.getLogger(__name__)


class FanSensor(object):
    """ Simple data about a sensor. These sensors are all related to auto-fan
    and may not be on the fan controller proper. (Most are not).
    """
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
    """ Collection of all sensors on a single VEC read by auto-fan. This
    represents a single read of all sensors except the ones on the fan
    controller itself.
    """

    # Maximum number of supported thermistors.
    SUPPORTED_THERMISTOR_COUNT = 12
    # Maximum number of supported differential pressure sensors..
    SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT = 3

    def __init__(self):
        """ Initialize the FanSensors object which is used for the fan_sensors
        route for auto fan.
        """
        # We need to differ initialization until after app_config['DEVICES'] is
        # setup (all devices are registered).
        self.initialized = False
        self.app_config = None
        self.start_time = None
        self.end_time = None
        self.read_time = None
        self.thermistor_devices = None
        self.thermistors = None
        self.differential_pressure_devices = None
        self.differential_pressures = None
        self.thermistor_read_count = None
        self.differential_pressure_read_count = None
        self.from_background = None

    def initialize(self, app_config):
        """ Initialize the FanSensors object which is used for the fan_sensors
        route for auto fan.

        Args:
            app_config: Flask app.config.
        """

        if self.initialized:
            return

        if 'DEVICES' not in app_config:
            logger.debug('Unable to initialize FanSensors since all devices are not '
                         'yet registered.')
            return  # We need to wait for all devices to register.

        self.app_config = app_config

        # Reading info
        self.start_time = None
        self.end_time = None
        self.read_time = None

        # From i2c.

        # FUTURE: We should probably do this the way the i2c daemon does it by reading
        # the synse config.

        # FUTURE: All thermistors need the same device_name to support bulk reads.
        # It doesn't matter now since we're not even using device_name from the synse
        # config for production i2c sensor reads. Also true for differential pressure
        # (i2c as well).
        self.thermistor_devices = self._find_devices_by_instance_name(
            Max11608Thermistor.get_instance_name())
        # List length FanSensors.SUPPORTED_THERMISTOR_COUNT, all entries are None.
        self.thermistors = [None] * FanSensors.SUPPORTED_THERMISTOR_COUNT
        for d in self.thermistor_devices:
            channel = d.channel
            self.thermistors[channel] = FanSensor('thermistor_{}'.format(channel), 'C', d)

        self.differential_pressure_devices = \
            self._find_devices_by_instance_name(SDP610Pressure.get_instance_name())
        # List length SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT, all entries are None.
        self.differential_pressures = [None] * FanSensors.SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT
        for d in self.differential_pressure_devices:
            channel = d.channel
            channel_ordinal = i2c_common.get_channel_ordinal(channel)
            self.differential_pressures[channel_ordinal] = \
                FanSensor('differential_pressure_{}'.format(channel_ordinal), 'Pa', d)

        # Compute the number of thermistors and differential pressure sensors to read.
        self.thermistor_read_count = self._thermistor_read_count()
        self.differential_pressure_read_count = self._differential_pressure_read_count()

        # Direct or indirect sensor reads.
        self.from_background = FanSensors._get_from_background()

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
        for dp in self.differential_pressures:
            if dp is not None:
                dp.reading = None

    def _differential_pressure_read_count(self):
        """ Determine the number of differential pressure sensors to read on each
        `_read_differential_pressures` call.

        Returns:
            The number of differential pressure sensors to read on each
            call.
        """
        # Find the maximum channel for each differential pressure sensor.
        # Compute ordinal.
        max_channel = -1
        for dpressure in self.differential_pressures:
            if dpressure is not None and dpressure.device is not None:
                if dpressure.device.channel > max_channel:
                    max_channel = dpressure.device.channel

        result = i2c_common.get_channel_ordinal(max_channel)
        result += 1
        if result > FanSensors.SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT:
            raise ValueError('Unsupported differential pressure sensor count {}. Maximum {}'.format(
                result, FanSensors.SUPPORTED_DIFFERENTIAL_PRESSURE_COUNT))
        return result

    def _dump(self):
        """ Dump all fan sensors to the log so that we can see what we are
        doing.
        """
        logger.debug('Dumping FanSensors:')
        for t in self.thermistors:
            logger.debug('thermistor:  {}'.format(t))
        for dp in self.differential_pressures:
            logger.debug('pressure:  {}'.format(dp))
        logger.debug('thermistor read count {}'.format(self.thermistor_read_count))
        logger.debug('d pressure read count {}'.format(self.differential_pressure_read_count))
        logger.debug('self.from_background: {}'.format(self.from_background))

    def _find_devices_by_instance_name(self, instance_name):
        """ Used on initialization to find a device by class name.

        Args:
            instance_name: The device model to check for.

        Returns
            A list of all devices of the_type.
        """
        logger.debug('_find_devices_by_instance_name')
        result = []
        devices = self.app_config['DEVICES']
        for d in devices.values():
            if d.__class__.get_instance_name() == instance_name:
                result.append(d)
        return result

    # TODO: We need configuration testing here.
    # TODO: from_background should probably be per synse instance, not per rack.
    @staticmethod
    def _get_from_background():
        """ Read in the from_background setting from the synse configuration.
        It's defined at the per rack level. Ideally all are the same.
        """
        from_background = None
        i2c_config = FanSensors._get_i2c_config()
        for rack in i2c_config['racks']:
            background_setting = rack.get('from_background', None)
            if background_setting is not None:
                if from_background is None:
                    from_background = background_setting
                else:
                    if from_background != background_setting:
                        logger.error(
                            'i2c configuration error. from_background is {}, ignoring '
                            'new setting {}'.format(from_background, background_setting)
                        )
        if from_background is None:
            from_background = False
        logger.info('from_background: {}'.format(from_background))
        return from_background

    @staticmethod
    def _get_i2c_config():
        """Get the configuration from the Synse i2c config file."""
        cfg = ConfigManager(
            default='/synse/default/default.json',
            override='/synse/override'
        )

        # Find the location of the Synse configuration file.
        location = cfg['devices']['i2c']['from_config']
        logger.debug('i2c_config file location: {}'.format(location))
        # Read the Synse configuration file.
        with open(location) as config:
            i2c_config = json.load(config)
            return i2c_config

    def _read_thermistors(self):
        """Read the configured thermistors."""
        if self.from_background:
            self._read_thermistors_indirect()
        else:
            self._read_thermistors_direct()

    def _read_thermistors_direct(self):
        """Read the configured thermistors by hitting the bus."""
        readings = i2c_common.read_thermistors(self.thermistor_read_count)
        for i, reading in enumerate(readings):
            self.thermistors[i].reading = reading

    def _read_thermistors_indirect(self):
        """Read the configured thermistors without hitting the bus."""
        for t in self.thermistor_devices:
            channel = t.channel
            data = t.indirect_sensor_read()[const.UOM_TEMPERATURE]
            self.thermistors[channel].reading = data
        logger.debug('_read_thermistors_indirect: {}'.format(self.thermistors))

    def _read_differential_pressures(self):
        """Read the configured differential pressure sensors."""
        if self.from_background:
            self._read_differential_pressures_indirect()
        else:
            self._read_differential_pressures_direct()

    def _read_differential_pressures_direct(self):
        """Read the configured differential pressure sensors by hitting the bus."""
        readings = i2c_common.read_differential_pressures(self.differential_pressure_read_count)
        for i, reading in enumerate(readings):
            self.differential_pressures[i].reading = reading

    def _read_differential_pressures_indirect(self):
        """Read the configured differential pressure sensors without hitting the bus."""
        for dp in self.differential_pressure_devices:
            channel = dp.channel
            ordinal = i2c_common.get_channel_ordinal(channel)
            data = dp.indirect_sensor_read()[const.UOM_PRESSURE]
            self.differential_pressures[ordinal].reading = data
        logger.debug('_read_diff_pressures_indirect: {}'.format(self.differential_pressures))

    def _thermistor_read_count(self):
        """ Determine the number of thermistors to read on each
        `_read_thermistors` call.

        Returns:
            The number of thermistors to read on each call.
        """
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
