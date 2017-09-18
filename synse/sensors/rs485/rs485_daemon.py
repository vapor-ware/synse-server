#!/usr/bin/env python
"""
    \\//
     \/apor IO

     The rs485_daemon is currently a background process that lives in the Synse
     container. It is only active on the vec leader. It reads RS485 sensors
     independently of Synse and writes the data read to well known file
     locations based on the Synse configuration. This provides bus ownership
     and eliminates contention and lag when a Synse call comes in to read an
     RS485 sensor.
"""

import json
import logging
import os
import serial
import time
from synse.protocols.conversions import conversions
from synse.protocols.modbus import dkmodbus
from synse.sensors import common
from synse.vapor_common.vapor_config import ConfigManager
from synse.vapor_common.vapor_logging import setup_logging

# Base path to write the sensor data to.
BASE_FILE_PATH = '/synse/sensors/'
RS485_DIR_PATH = BASE_FILE_PATH + 'rs485/{}/{}/{}/{}'  # rack_id, device_model, device_unit, base_address
RS485_FILE_PATH = RS485_DIR_PATH + '/{}'  # rack_id, device_model, device_unit, base_address, {read | write}

READ = 'read'
WRITE = 'write'

logger = logging.getLogger(__name__)


class FanInfo(object):
    """Contains information we need for writes to the vapor_fan."""

    def __init__(self, rs485_config):
        """Initialize the FanInfo from the rs485_config.
        :param rs485_config: Synse rs485 configuration."""
        for rack in rs485_config['racks']:
            devices = rack['devices']
            for device in devices:
                if device['device_type'] == 'vapor_fan':
                    path = RS485_FILE_PATH.format(
                       rack['rack_id'], device['device_model'], device['device_unit'], device['base_address'], WRITE)

                    self.serial_device = rack['device_name']    # For serial connection to the fan.
                    self.device = device                        # Device config for the fan.
                    self.path = path                            # Write speed file path for the fan.

                    logger.debug('FanInfo: self.serial_device {}'.format(self.serial_device))
                    logger.debug('FanInfo: self.device        {}'.format(self.device))
                    logger.debug('FanInfo: self.path          {}'.format(self.path))
                    return  # Success

        raise ValueError('No vapor_fan in rs485 configuration.')   # Game over


def _create_device_directories(rs485_config):
    """Create directories for sensor read/write files.
    :param rs485_config: The Synse rs485 configuration."""
    for rack in rs485_config['racks']:
        devices = rack['devices']
        for device in devices:
            logger.debug('device: {}'.format(device))
            path = RS485_DIR_PATH.format(
                rack['rack_id'], device['device_model'], device['device_unit'], device['base_address'])
            logger.debug('Creating directory: {}'.format(path))
            common.mkdir(path)


def _create_modbus_client(serial_device, device):
    """Production hardware only wrapper for creating the serial device that
     we use to speak modbus to the CEC (Central Exhaust Chamber) board.
     This will not work for the emulator.
     :param serial_device: The serial device for modbus, example /dev/ttyUSB3.
     :param device: The device configuration from the Synse config.
     :returns: The dkmodbus client."""
    # Test that the usb device is there. If not, reset the usb.
    if not os.path.exists(serial_device):
        dkmodbus.dkmodbus.reset_usb([1, 2])

    timeout = device.get('timeout', 0.15)
    ser = serial.Serial(
        serial_device,  # Serial device name.
        baudrate=device['baud_rate'],
        parity=device['parity'],
        timeout=timeout)
    return dkmodbus.dkmodbus(ser)


def _get_gs32010_rpm(serial_device, device):
    """Production only rpm reads from gs3_2010_fan (vapor_fan).
    :param serial_device: The serial device name.
    :param device: The device to read.
    :returns: Integer rpm."""
    client = _create_modbus_client(serial_device, device)
    result = client.read_holding_registers(int(device['device_unit']), 0x2107, 1)
    return conversions.unpack_word(result)


def _get_gs32010_direction(serial_device, device):
    """Production only direction reads from gs3_2010_fan (vapor_fan).
    :param serial_device: The serial device name.
    :param device: The device to read.
    :returns: String forward or reverse."""
    client = _create_modbus_client(serial_device, device)
    result = client.read_holding_registers(int(device['device_unit']), 0x91C, 1)
    direction = conversions.unpack_word(result)
    if direction == 0:
        return 'forward'
    elif direction == 1:
        return 'reverse'
    else:
        raise ValueError('Unknown direction {}'.format(direction))


def _get_rs485_config():
    """Get the configuration from the Synse rs485 config file."""
    cfg = ConfigManager(
        default='/synse/default/default.json',
        override='/synse/override'
    )

    # if no rs485 is configured, no config to get.
    if 'rs485' not in cfg['devices']:
        return None

    # Find the location of the Synse configuration file.
    location = cfg['devices']['rs485']['from_config']
    logger.debug('rs485_config file location: {}'.format(location))
    # Read the Synse configuration file.
    with open(location) as config:
        rs485_config = json.load(config)
        return rs485_config


def _handle_fan_speed_write(fan_info):
    """If there is a pending write to the fan speed, write the change to the
    fan. This may come in as None.
    :param fan_info: All information we need to write out the fan speed to the
    bus."""
    if fan_info is None:
        return # Nothing to do
    try:
        logger.debug('_handle_fan_speed_write')
        if os.path.isfile(fan_info.path):
            logger.debug('writing fan speed, path: {}'.format(fan_info.path))
            # Read the file it should contain the speed in rpm.
            # Write the speed to the fan. Delete the file on success.
            with open(fan_info.path, 'r') as f:
                speed = f.read()
            logger.debug('writing fan speed: {}.'.format(speed))
            _set_fan_rpm(fan_info.serial_device, fan_info.device, speed)
            os.remove(fan_info.path)
    except:
        logger.exception('Error writing fan speed.')
    pass


def _is_vec_leader():
    """Return true if this VEC is the leader, else false.
    :returns: True if this VEC is the leader, else False."""
    with open('/crate/mount/.state-file') as f:
        data = json.load(f)
        if data['VAPOR_VEC_LEADER'] == data['VAPOR_VEC_IP']:
            return True
    return False


def _read_device_by_model(rack_id, serial_device, device):
    """Farm out the bus read based on device['device_model'].
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    try:
        device_model = device.get('device_model')
        if device_model == 'gs3-2010':
            _read_gs32010_fan_speed(rack_id, serial_device, device)
        elif device_model == 'sht31':
            _read_sht31_humidity(rack_id, serial_device, device)
        elif device_model == 'f660':
            _read_f660_airflow(rack_id, serial_device, device)
        else:
            logger.error('Unsupported device model: {}'.format(device_model))

    except:
        logger.exception('rs485_daemon read exception')


def _read_f660_airflow(rack_id, serial_device, device):
    """Read the airflow from the bus. Write it to the sensor file.
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    client = _create_modbus_client(serial_device, device)
    result = client.read_input_registers(int(device['device_unit']), int(device['base_address']), 1)
    airflow = conversions.airflow_f660(result)
    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_reading(path, airflow)


def _read_gs32010_fan_speed(rack_id, serial_device, device):
    """Read the fan speed from the bus. Write it to the sensor file.
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    rpm = _get_gs32010_rpm(serial_device, device)
    direction = _get_gs32010_direction(serial_device, device)

    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_readings(path, [rpm, direction])


def _read_sht31_humidity(rack_id, serial_device, device):
    """Read the temperature and humidity from the bus. Write them to the sensor
    file.
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    client = _create_modbus_client(serial_device, device)
    result = client.read_input_registers(int(device['device_unit']), int(device['base_address']), 2)
    temperature = conversions.temperature_sht31(result)
    humidity = conversions.humidity_sht31(result)
    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_readings(path, [temperature, humidity])


def _set_fan_rpm(serial_device, device, rpm):
    """Set fan speed to the given RPM by calling out to the bus.
    :param serial_device: The serial device name.
    :param device: The vapor_fan device.
    :param rpm: The fan speed setting in RPM.
    :returns: The fan speed setting in RPM."""
    client = _create_modbus_client(serial_device, device)
    if rpm == 0:  # Turn the fan off.
        result = client.write_multiple_registers(
            int(device['device_unit']),  # Slave address.
            0x91B,  # Register to write to.
            1,  # Number of registers to write to.
            2,  # Number of bytes to write.
            '\x00\x00')  # Data to write.

    else:  # Turn the fan on at the desired RPM.
        packed_hz = conversions.fan_gs3_2010_rpm_to_packed_hz(rpm)

        result = client.write_multiple_registers(
            int(device['device_unit']),  # Slave address.
            0x91A,  # Register to write to.
            2,  # Number of registers to write to.
            4,  # Number of bytes to write.
            packed_hz + '\x00\x01')  # Frequency setting in Hz / data # 01 is on, # 00 is off.

    return result


def _sensor_loop(rs485_config, fan_info):
    """Read sensors and write readings to sensor files.
    :param rs485_config: The Synse rs485 configuration.
    :param fan_info: All information we need to be able to write the fan speed
    setting to the bus."""
    _create_device_directories(rs485_config)

    # Wait for synse to register all devices. Synse needs to do that since
    # there is no guarantee that the background processes are being used.
    # TODO: Tune time to sleep. Ideally synse would signal, but we don't want a
    # Synse dependency here.
    time.sleep(10)

    while True:
        _handle_fan_speed_write(fan_info)

        # TODO: Metrics around the reads here.
        for rack in rs485_config['racks']:
            serial_device = rack['device_name']
            devices = rack['devices']
            for device in devices:
                _read_device_by_model(rack['rack_id'], serial_device, device)
        # END: Metrics around the reads here.

        time.sleep(1)  # TODO: tuning. Allows time for other tools (gs3fan) to get in direct reads/writes.


def _wait_until_leader():
    """Wait until this vec is the leader."""
    logged = False
    while not _is_vec_leader():
        if not logged:
            logger.info('Waiting until we are VEC leader.')
            logged = True
        time.sleep(1)
    logger.info('We are VEC leader.')


def main():
    try:
        setup_logging(default_path='/synse/configs/logging/synse.json')
        logger.info('Starting rs485_daemon')

        # Read and dump synse configuration.
        rs485_config = _get_rs485_config()
        logger.debug('rs485_config:')
        logger.debug(json.dumps(rs485_config, sort_keys=True, indent=4, separators=(',', ': ')))

        if rs485_config is None:
            logger.info('No RS485 config set - terminating RS485 daemon.')

        # TODO: from_background should be at the same level as racks. (once per config file)
        # Daemons and straight bus reads from a web client will collide.
        # Also - these daemons only work on production hardware.
        # Turning on background reads for i2c without rs485 and vice versa will not cause bus collisions.
        # They are separate buses.
        from_background = False
        for rack in rs485_config['racks']:
            if rack.get('from_background', False):
                from_background = True
                break
        if not from_background:
            logger.debug('No background sensor reads. Exiting.')
            return

        _wait_until_leader()    # This only fully runs on the vec leader. (Shared bus.)

        # Setup information for fan speed writes.
        fan_info = None
        try:
            fan_info = FanInfo(rs485_config)
        except ValueError:
            logger.exception('No fan controller.')

        _sensor_loop(rs485_config, fan_info)

    except:
        logger.exception('Fatal exception in rs485_daemon.')

if __name__ == '__main__':
    main()
