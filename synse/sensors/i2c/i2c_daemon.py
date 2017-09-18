#!/usr/bin/env python
"""
    \\//
     \/apor IO

     The i2c_daemon is currently a background process that lives in the Synse
     container. It reads I2C sensors independently of Synse and writes the
     data read to well known file locations based on the Synse configuration.
     This provides bus ownership and eliminates contention and lag when a Synse
     call comes in to read an I2C sensor.
"""

import json
import logging
import os
import time
from synse.protocols.i2c_common import i2c_common
from synse.sensors import common
from synse.vapor_common.vapor_config import ConfigManager
from synse.vapor_common.vapor_logging import setup_logging

# Constants

# List of all I2C thermistor sensor models.
THERMISTOR_MODELS = ['max-11608']

# List of all I2C differential pressure sensor models.
DIFFERENTIAL_PRESSURE_MODELS = ['sdp-610']

# List of all I2C LED Controller models.
LED_CONTROLLER_MODELS = ['pca-9632']

# Base path to write the sensor data to.
BASE_FILE_PATH = '/synse/sensors/'
I2C_DIR_PATH = BASE_FILE_PATH + 'i2c/{}/{}/{}'  # rack_id, device_model, channel
I2C_FILE_PATH = I2C_DIR_PATH + '/{}'  # rack_id, device_model, channel, {read | write}

READ = 'read'
WRITE = 'write'

logger = logging.getLogger(__name__)


class LedInfo(object):
    """Contains information we need for writes to the vapor_led."""
    def __init__(self, i2c_config):
        """Initialize the LedInfo from the information.
        :param i2c_config: Synse i2c configuration."""
        for rack in i2c_config['racks']:
            devices = rack['devices']
            for device in devices:
                if device['device_type'] == 'vapor_led':
                    path = I2C_FILE_PATH.format(
                       rack['rack_id'], device['device_model'], device['channel'], WRITE)

                    self.device = device                        # Device config for the LED controller.
                    self.path = path                            # Write file path for the LED controller.

                    logger.debug('LedInfo: self.device        {}'.format(self.device))
                    logger.debug('LedInfo: self.path          {}'.format(self.path))
                    return  # Success

        raise ValueError('No vapor_led in i2c configuration.')


def _bulk_read_differential_pressure(differential_pressures, channels):
    """Bulk read differential pressure sensors and write the results to files.
    :param differential_pressures: Dictionary of rack_id, device from the Synse
    i2c config. Differential pressure sensors are the device section of the
    config.
    :param channels: A list of rack id keys and sorted differential
    pressure sensor channels per rack."""
    try:
        for rack_id, channels in channels.iteritems():

            # Perform the read and the math for turbulence.
            channel_count = len(channels)
            if channel_count > 0:
                readings = i2c_common.read_differential_pressures(channel_count)

                # Write out the file.
                dps = differential_pressures[rack_id]
                for index, reading in enumerate(readings):

                    channel = _get_channel_from_ordinal(index)
                    # Find the sensor in order to create the path.
                    # TODO: There may be an issue here when the synse config is not
                    # sorted by channel? (Need the test.)
                    for dp in dps:
                        if int(dp['channel']) == channel:
                            # This is it. Create the path and write.
                            path = I2C_FILE_PATH.format(
                                rack_id, dp['device_model'], dp['channel'], READ)
                            common.write_reading(path, reading)
    except:
        logger.exception('Error reading differential pressure sensors.')


def _bulk_read_thermistors(thermistors, channels):
    """Bulk read thermistors and write the results to files.
    :param thermistors: Dictionary of rack_id, device from the Synse i2c
    config. Thermistors are the device section of the config.
    :param channels: A list of rack id keys and sorted thermistor
    channels per rack."""
    try:
        for rack_id, channels in channels.iteritems():
            # Read the thermistors.
            if len(channels) > 0:
                max_channel = channels[-1]  # channels is sorted low to high.
                readings = i2c_common.read_thermistors(max_channel + 1)

                # Write out the file.
                therms = thermistors[rack_id]
                for channel, reading in enumerate(readings):

                    # Find the thermistor in order to create the path.
                    for thermistor in therms:
                        if int(thermistor['channel']) == channel:
                            # This is it. Create the path to get the write.
                            path = I2C_FILE_PATH.format(
                                rack_id, thermistor['device_model'], thermistor['channel'], READ)
                            common.write_reading(path, reading)
    except:
        logger.exception('Error reading thermistors.')


def _create_device_directories(devices):
    """Create directories for sensor files.
    :param devices: Dictionary of rack_id, devices from the Synse i2c
    config."""
    for rack_id, devs in devices.iteritems():
        for device in devs:
            # TODO: Swap rack_id and device_model order?
            path = I2C_DIR_PATH.format(rack_id, device['device_model'], device['channel'])
            common.mkdir(path)


def _get_channel_from_ordinal(ordinal):
    """The differential pressure sensors have a channel setting that uses a
    bit shift.
    :raises: ValueError on invalid channel."""
    channels = [1, 2, 4, 8, 16, 32, 64, 128]
    return channels[ordinal]


def _get_device_channels(devices):
    """Given devices, return a dictionary with the rack_id as key and the list
    of channels as values.
    :param devices: A dictionary with key rack id, and values of devices.
    :returns: A dictionary of rack_id: [channels] where channels is a list of
    channel ordinals for the device_model in the Synse configuration."""
    result = {}
    for rack_id, dev in devices.iteritems():
        channels = []
        for device in dev:
            channels.append(int(device['channel']))
        channels.sort()
        result[rack_id] = channels
    return result


def _get_devices_by_models(i2c_config, device_models):
    """Get all devices in device_models from all racks from the Synse i2c configuration.
    :param i2c_config: The Synse i2c configuration.
    :param device_models: A list of device models to match.
    :returns: A dictionary of rack ids as keys and devices as values."""
    result = {}
    for rack in i2c_config['racks']:
        rack_id = rack['rack_id']
        devices = []
        for device in rack['devices']:
            if device['device_model'] in device_models:
                devices.append(device)
        result[rack_id] = devices
    return result


def _get_i2c_config():
    """Get the configuration from the Synse i2c config file."""
    # Vapor configuration manager for Synse.
    cfg = ConfigManager(
        default='/synse/default/default.json',
        override='/synse/override'
    )

    # if no i2c is configured, no config to get.
    if 'i2c' not in cfg['devices']:
        return None

    # Find the location of the Synse configuration file.
    location = cfg['devices']['i2c']['from_config']
    logger.debug('i2c_config file location: {}'.format(location))
    # Read the Synse configuration file.
    with open(location) as config:
        i2c_config = json.load(config)
        return i2c_config


def _handle_led_write(led_info):
    """If there is a pending write to the LED controller, write the change to the
    fan.
    :param led_info: All information we need to write out the led data to the
    bus. This may come in as None if not initialized."""
    if led_info is None:
        return  # Nothing to do.
    try:
        logger.debug('_handle_led_write')
        if os.path.isfile(led_info.path):
            logger.debug('writing led info, path: {}'.format(led_info.path))
            # Read the file. It should contain the state and possibly color and blink.
            # Write the data to the LCD controller. Delete the file on success.
            with open(led_info.path, 'r') as f:
                contents = f.read()
                data = contents.split()
                logger.debug('writing led info, file data: {}'.format(data))
                length = len(data)
                if not (length == 1 or length == 3):
                    logger.error('Invalid LED write data {}, discarding.'.format(data))
                    os.remove(led_info.path)
                    return

                state = data[0]
                if length == 1:
                    color = None
                    blink = None
                else:
                    color = data[1]
                    blink = data[2]

                logger.debug(
                    'writing led info: state {}, color {}, blink {}.'.format(
                        state, color, blink))
                i2c_common.write_led(state=state, blink_state=blink, color=color)
            os.remove(led_info.path)
    except:
        logger.exception('Error writing fan speed.')
    pass


def _read_led_controllers(led_controllers):
    """Read from the LED controllers and write the results to files.
    There should only be one per wedge.
    :param led_controllers: Dictionary of rack_id, device from the Synse i2c
    config. LED controllers are the device section of the config."""
    try:
        logger.debug('led_controllers: {}'.format(led_controllers))
        for rack_id, controllers in led_controllers.iteritems():
            for controller in controllers:
                state, color, blink = i2c_common.read_led()

                logger.debug('_read_led_controllers() state: {}, color: {}, blink: {}'.format(state, color, blink))
                # Get the file path.
                path = I2C_FILE_PATH.format(
                    rack_id, controller['device_model'], controller['channel'], READ)
                common.write_readings(
                    path, [state, color, blink])
    except:
        logger.exception('Error reading led controllers.')


def _sensor_loop(thermistors, thermistor_channels,
                 differential_pressures, differential_pressure_channels,
                 led_controllers, led_info):
    """Read / Write sensors. Write readings to files. Send writes from files.
    :param thermistors: Dictionary of rack_id, device from the Synse i2c
    config. Thermistors are the device section of the config.
    :param thermistor_channels: A list of rack id keys and sorted thermistor
    channels per rack.
    :param differential_pressures: Dictionary of rack_id, device from the Synse
    i2c config. Differential pressure sensors are the device section of the
    config.
    :param differential_pressure_channels: A list of rack id keys and sorted
    differential pressure sensor channels per rack.
    :param led_controllers: Dictionary of rack_id, device from the Synse
    i2c config. LED controllers are the device section of the config.
    :param led_info: Everything we need to send a write to the Led Controller."""
    # Make directories for the sensor files.
    _create_device_directories(thermistors)
    _create_device_directories(differential_pressures)
    _create_device_directories(led_controllers)

    # Wait for synse to register all devices. Synse needs to do that since
    # there is no guarantee that the background processes are being used.
    # TODO: Tune time to sleep. Ideally synse would signal, but we don't want a
    # Synse dependency here.
    time.sleep(10)

    # NOTE: Differential pressure sensor configuration (to 9 bit from 12 bit default)
    # is done by Synse.

    while True:
        try:
            _handle_led_write(led_info)

            # TODO: Metrics around the reads here.
            _bulk_read_thermistors(thermistors, thermistor_channels)
            _bulk_read_differential_pressure(differential_pressures, differential_pressure_channels)
            _read_led_controllers(led_controllers)
            # END: Metrics around the reads here.
        except:
            logger.exception('i2c_daemon _sensor_loop() exception')
        time.sleep(1)  # TODO: tuning.


def main():
    """Read I2C sensors based off of the Synse I2C configuration in a loop.
    Write the results to files in a well known location."""
    try:
        # Log to the same location as Synse for starters.
        setup_logging(default_path='/synse/configs/logging/synse.json')
        logger.info('Starting i2c_daemon')

        # Read and dump synse configuration.
        i2c_config = _get_i2c_config()
        logger.debug('i2c_config:')
        logger.debug(json.dumps(i2c_config, sort_keys=True, indent=4, separators=(',', ': ')))

        if i2c_config is None:
            logger.info('No I2C config set - terminating I2C daemon.')
            return

        # TODO: from_background should be at the same level as racks. (once per config file)
        # Daemons and straight bus reads from a web client will collide.
        # Also - these daemons only work on production hardware.
        # Turning on background reads for i2c without rs485 and vice versa will not cause bus collisions.
        # They are separate buses.
        from_background = False
        for rack in i2c_config['racks']:
            if rack.get('from_background', False):
                from_background = True
                break
        if not from_background:
            logger.debug('No background sensor reads. Exiting.')
            return

        # Get the thermistors and differential pressure sensors from the configuration.
        thermistors = _get_devices_by_models(i2c_config, THERMISTOR_MODELS)
        differential_pressures = _get_devices_by_models(i2c_config, DIFFERENTIAL_PRESSURE_MODELS)
        led_controllers = _get_devices_by_models(i2c_config, LED_CONTROLLER_MODELS)

        # Get the channels for the thermistors and differential pressure sensors.
        thermistor_channels = _get_device_channels(thermistors)
        differential_pressure_channels = _get_device_channels(differential_pressures)
        # We are note using the channel from the sysne configuration for the LED Controller.

        # Setup information for LED Controller writes.
        led_info = None
        try:
            led_info = LedInfo(i2c_config)
        except ValueError:
            logger.exception('No led controller.')

        # Read sensors in a loop.
        _sensor_loop(
            thermistors, thermistor_channels,
            differential_pressures,  differential_pressure_channels,
            led_controllers, led_info)
    except:
        logger.exception('Fatal exception in i2c_daemon.')


if __name__ == '__main__':
    main()
