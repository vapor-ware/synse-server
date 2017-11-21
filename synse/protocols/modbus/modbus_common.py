#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Common file for modbus operations to avoid cut and paste.
        gs3 command line tool and the synse device bus use this code. 
"""

from synse.protocols.modbus import dkmodbus  # nopep8
from synse.protocols.conversions import conversions  # nopep8


def get_fan_frequency_gs3(ser):
    """Get the base (max) frequency of the fan motor through the gs3 fan
    controller.
    :param ser: Serial connection to the gs3 fan controller.
    :returns: The base motor frequency.
    """
    return read_holding_register(ser, 0x0002)


def get_ebmpapst_rpm(serial_device, device):
    """Production only rpm reads from Ebm Papst fan (vapor_fan).
    :param serial_device: The serial device name.
    :param device: The device to read.
    :returns: Integer rpm."""
    raise NotImplementedError('Need to get the correct register readings.')
    # client = _create_modbus_client(serial_device, device)
    # result = client.read_input_registers(
    #     int(device['device_unit']),  # Slave address
    #     0xD010,                      # Register
    #     1)                           # Register count
    # # TODO: May be a conversion here? Unclear.
    # return conversions.unpack_word(result)


def get_ebmpapst_direction(serial_device, device):
    """Production only direction reads from Ebm Papst fan (vapor_fan).
    :param serial_device: The serial device name.
    :param device: The device to read.
    :returns: String forward or reverse."""
    raise NotImplementedError('Need to get the correct register readings.')
    # client = _create_modbus_client(serial_device, device)
    # result = client.read_input_registers(
    #     int(device['device_unit']),  # Slave address
    #     0xD010,                      # Register
    #     1)                           # Register count
    # direction = conversions.unpack_word(result)
    # if direction == 0:
    #     # TODO: This is counter-clockwise.
    #     return 'forward'
    # elif direction == 1:
    #     # TODO: This is clockwise.
    #     return 'reverse'
    # else:
    #     raise ValueError('Unknown direction {}'.format(direction))


def get_fan_rpm_to_hz_gs3(ser, max_rpm):
    """Get the conversion from rpm to hertz. The operator sets the fan speed in
    rpm. The fan controller sets the fan speed in hertz.
    :param ser: Serial connection to the gs3 fan controller.
    :param max_rpm: The maximum rpm of the fan motor.
    :returns: The conversion from rpm to hertz.
    """
    base_frequency = get_fan_frequency_gs3(ser)
    return float(base_frequency) / float(max_rpm)


def get_fan_max_rpm_ebm(ser):
    """Get the maximum rpm of the fan motor through the ebm fan controller.
    :param ser: Serial connection to the ebm fan controller.
    :returns: The base maximum rpm of the fan motor.
    """
    return read_holding_register(ser, 0xD119)


def get_fan_max_rpm_gs3(ser):
    """Get the maximum rpm of the fan motor through the gs3 fan controller.
    :param ser: Serial connection to the gs3 fan controller.
    :returns: The base maximum rpm of the fan motor.
    """
    return read_holding_register(ser, 0x0004)


def read_holding_register(ser, register):
    """Read a holding register from the fan controller.
    :param ser: Serial connection to the fan controller.
    :param register: The register to read (int).
    :returns The register reading (int).
    """
    client = dkmodbus.dkmodbus(ser)
    register_data = client.read_holding_registers(1, register, 1)
    result = conversions.unpack_word(register_data)
    print '0x{}'.format(result)
    return result


def read_input_register(ser, register):
    """Read an input register from the fan controller.
    :param ser: Serial connection to the fan controller.
    :param register: The register to read (int).
    :returns The register reading (int).
    """
    client = dkmodbus.dkmodbus(ser)
    register_data = client.read_input_registers(1, register, 1)
    result = conversions.unpack_word(register_data)
    print '0x{}'.format(result)
    return result
