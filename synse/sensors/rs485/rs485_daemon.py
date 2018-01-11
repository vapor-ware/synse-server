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

# pylint: disable=bare-except

import json
import logging
import os
import serial
import time
import requests

from synse.protocols.conversions import conversions
from synse.protocols.modbus import dkmodbus
from synse.protocols.modbus import modbus_common  # nopep8
from synse.sensors import common
from synse.vapor_common.vapor_config import ConfigManager
from synse.vapor_common.vapor_logging import setup_logging

# Base path to write the sensor data to.
BASE_FILE_PATH = '/synse/sensors/'
# rack_id, device_model, device_unit, base_address
RS485_DIR_PATH = BASE_FILE_PATH + 'rs485/{}/{}/{}/{}'
# rack_id, device_model, device_unit, base_address, {read | write}
RS485_FILE_PATH = RS485_DIR_PATH + '/{}'

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
                        rack['rack_id'], device['device_model'],
                        device['device_unit'], device['base_address'], WRITE)

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
                rack['rack_id'], device['device_model'],
                device['device_unit'], device['base_address'])
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
    return modbus_common.get_fan_rpm_gs3(client.serial_device, int(device['device_unit']))


def _get_gs32010_direction(serial_device, device):
    """Production only direction reads from gs3_2010_fan (vapor_fan).
    :param serial_device: The serial device name.
    :param device: The device to read.
    :returns: String forward or reverse."""
    client = _create_modbus_client(serial_device, device)
    return modbus_common.get_fan_direction_gs3(
        client.serial_device, int(device['device_unit']))


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
        return  # Nothing to do
    try:
        logger.debug('_handle_fan_speed_write')
        if os.path.isfile(fan_info.path):
            logger.debug('writing fan speed, path: {}'.format(fan_info.path))
            # Read the file it should contain the speed in rpm.
            # Write the speed to the fan. Delete the file on success.
            with open(fan_info.path, 'r') as f:
                speed = int(f.read())
            logger.debug('writing fan speed: {}.'.format(speed))
            _set_fan_rpm(fan_info.serial_device, fan_info.device, speed)
            os.remove(fan_info.path)
    except:
        logger.exception('Error writing fan speed.')


def _is_vec_leader_crate_stack():
    """Return true if this VEC is the leader, else False.
    :returns: True if this VEC is the leader, else False."""
    with open('/crate/mount/.state-file') as f:
        data = json.load(f)
        if data['VAPOR_VEC_LEADER'] == data['VAPOR_VEC_IP']:
            logger.debug('is_vec_leader_crate_stack: True')
            return True
        logger.debug('is_vec_leader_crate_stack: False')
    return False


def _is_vec_leader_k8_stack():
    """Return true if this VEC is the leader, else False.
    :returns: True if this VEC is the leader, else False."""
    leader = _get_vec_leader_k8_stack()
    if leader is not None:
        self = os.environ['POD_IP']
        logger.debug('leader is: {}'.format(leader))
        logger.debug('self is: {}'.format(self))
        return self == leader

    return False


def _is_vec_leader():
    """Return true if this VEC is the leader, else False.
    :returns: True if this VEC is the leader, else False."""
    # Try the new stack first, then fall back to the old stack.
    is_leader = _is_vec_leader_k8_stack()
    if is_leader:
        return is_leader
    is_leader = _is_vec_leader_crate_stack()
    return is_leader


def _get_vec_leader_crate_stack():
    """Get the VEC leader when using the k8 stack. (old stack)
    :returns: The VEC leader IP address."""
    with open('/crate/mount/.state-file') as f:
        data = json.load(f)
        leader = data['VAPOR_VEC_LEADER']
        logger.debug('leader: {}'.format(leader))
        return leader


def _get_vec_leader_k8_stack():
    """Get the VEC leader when using the k8 stack. (new stack)
    :returns: The VEC leader IP address or None on failure."""
    # FIXME (etd) - we will probably want to be smarter about how we do this.
    #   for now, just making the request here, but perhaps we should have some
    #   sort of client with retries, etc.
    try:
        r = requests.get('http://elector-headless:2288/status')
        logger.debug('request for vec leader: {}'.format(r))
        leader = None
        if r.ok:
            data = r.json()
            logger.debug('data: {}'.format(data))
            for k, v in data['members'].iteritems():
                if v == 'leader':
                    leader = k
                    break
        else:
            logger.error('Could not determine the leader for k8 stack: {}'.format(r))
            return None
    except requests.exceptions.ConnectionError:
        logger.info('Unable to get vec leader from the k8 stack. Will try with the crate stack.')
        return None

    logger.debug('leader: {}'.format(leader))
    return leader


def _get_vec_leader():
    """Return the VEC leader IP address.
    :returns: The VEC leader IP address."""
    # Try the new stack first, then fall back to the old stack.
    leader = _get_vec_leader_k8_stack()
    if leader is not None:
        return leader
    return _get_vec_leader_crate_stack()


def _read_device_by_model(rack_id, serial_device, device):
    """Farm out the bus read based on device['device_model'].
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    try:
        device_model = device.get('device_model')
        if device_model == 'ecblue':
            _read_ecblue_fan_speed(rack_id, serial_device, device)
        elif device_model == 'gs3-2010':
            _read_gs32010_fan_speed(rack_id, serial_device, device)
        elif device_model == 'sht31':
            _read_sht31_humidity(rack_id, serial_device, device)
        elif device_model == 'f660':
            _read_f660_airflow(rack_id, serial_device, device)
        elif device_model == 'max-11608-ambient':
            _read_max11608_ambient(rack_id, serial_device, device)
        else:
            logger.error('Unsupported device model: {}'.format(device_model))

    except:
        logger.exception('rs485_daemon read exception')


def _read_ecblue_fan_speed(rack_id, serial_device, device):
    """Read the fan speed from the bus. Write it to the sensor file.
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read.
    """
    client = _create_modbus_client(serial_device, device)
    rpm = modbus_common.get_fan_rpm_ecblue(
        client.serial_device, int(device['device_unit']))
    direction = modbus_common.get_fan_direction_ecblue(
        client.serial_device, int(device['device_unit']))

    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_readings(path, [rpm, direction])


def _read_f660_airflow(rack_id, serial_device, device):
    """Read the airflow from the bus. Write it to the sensor file.
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    client = _create_modbus_client(serial_device, device)
    result = client.read_input_registers(
        int(device['device_unit']), int(device['base_address'], 16), 1)
    airflow = conversions.airflow_f660(result)
    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_reading(path, airflow)


def _read_max11608_ambient(rack_id, serial_device, device):
    """Read the airflow from the bus. Write it to the sensor file.
    :param rack_id: The rack_id from the Synse configuration.
    :param serial_device: The serial device name.
    :param device: The device to read."""
    client = _create_modbus_client(serial_device, device)
    result = client.read_input_registers(
        int(device['device_unit']), int(device['base_address'], 16), 1)
    temperature = conversions.thermistor_max11608_adc_49(result)
    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_reading(path, temperature)


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
    result = client.read_input_registers(
        int(device['device_unit']), int(device['base_address'], 16), 2)
    temperature = conversions.temperature_sht31(result)
    humidity = conversions.humidity_sht31(result)
    path = RS485_FILE_PATH.format(
        rack_id, device['device_model'], device['device_unit'], device['base_address'], READ)
    common.write_readings(path, [temperature, humidity])


def _set_fan_rpm(serial_device, device, rpm_setting):
    """Set fan speed to the given RPM by calling out to the bus.
    :param serial_device: The serial device name. Example: /dev/ttyUSB3
    :param device: The vapor_fan device. Example: class GS32010Fan
    :param rpm_setting: The fan speed setting in RPM.
    :returns: The modbus write result."""
    client = _create_modbus_client(serial_device, device)
    fan_model = device['device_model']

    if fan_model == 'ecblue':
        max_rpm = modbus_common.get_fan_max_rpm_ecblue(
            client.serial_device, int(device['device_unit']))
        return modbus_common.set_fan_rpm_ecblue(
            client.serial_device, int(device['device_unit']),
            rpm_setting, max_rpm)

    elif fan_model == 'gs3-2010':
        max_rpm = modbus_common.get_fan_max_rpm_gs3(
            client.serial_device, int(device['device_unit']))
        return modbus_common.set_fan_rpm_gs3(
            client.serial_device, int(device['device_unit']),
            rpm_setting, max_rpm)

    raise ValueError('Unknown fan model: {}.'.format(fan_model))


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

        # TODO: tuning. Allows time for other tools (gs3fan) to get in direct
        # reads/writes.
        time.sleep(1)


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
    """Main entry point."""
    try:
        setup_logging(default_path='/synse/configs/logging/synse.json')
        logger.info('Starting rs485_daemon')

        # Read and dump synse configuration.
        rs485_config = _get_rs485_config()
        logger.debug('rs485_config:')
        logger.debug(json.dumps(rs485_config, sort_keys=True, indent=4, separators=(',', ': ')))

        if rs485_config is None:
            logger.info('No RS485 config set - terminating RS485 daemon.')
            return

        # TODO: from_background should be at the same level as racks. (once per config file)
        # Daemons and straight bus reads from a web client will collide.
        # Also - these daemons only work on production hardware.
        # Turning on background reads for i2c without rs485 and vice versa will
        # not cause bus collisions.
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
