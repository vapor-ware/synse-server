#!/usr/bin/env python
"""
   OpenDCRE IPMI Bridge
   Uses pyghmi as back-end IPMI library (replaces old vapor_ipmi module).

   Author:  andrew
   Date:    6/16/2016

        \\//
         \/apor IO

Copyright (C) 2015-16  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
from pyghmi.ipmi import command
from errors import OpenDcreException


class _IpmiCommand(object):
    """
        Wrapper for IPMICommand that cleans up after itself.
    """
    o = None

    def __init__(self, username=None, password=None, ip_address=None):
        self.o = command.Command(userid=username, password=password, bmc=ip_address)

    def __enter__(self):
        return self.o

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.o:
            self.o.ipmi_session.logout()


def power(username=None, password=None, auth_type=None, ip_address=None, cmd=None, ipmi20_enabled=True,
          ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Get/set power status for remote host.

    Args:
        username: Username to connect to BMC with
        password: Password to connect to BMC with
        auth_type: Ignored
        ip_address: BMC IP Address
        cmd: "on", "off", "cycle", "status"
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: (dict) Power status after command execution, or raises IpmiException or InvalidParameterValue from pyghmi

    """
    # power cycle is hard reset in ipmi/pyghmi
    response = dict()
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        if cmd == 'status':
            result = ipmicmd.get_power()
        elif cmd == 'cycle':
            result = ipmicmd.get_power()
            # only power cycle if the machine is on
            if result['powerstate'] == 'on':
                ipmicmd.set_power('off', wait=True)
                result = ipmicmd.set_power('on', wait=True)
        else:
            result = ipmicmd.set_power(cmd, wait=True)
        if 'error' in result:
            raise OpenDcreException("Error executing IPMI power command on {} : {}".format(ip_address,
                                                                                            result['error']))
        response['power_status'] = result.get('powerstate', 'unknown')
        response['power_ok'] = True     # pyghmi does not return power_fault status
        return response


def sensors(username=None, password=None, auth_type=None, ip_address=None, ipmi20_enabled=True,
            ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Get list of sensors from remote system.

    Args:
        username: The username to use to connect to the remote BMC.
        password: The password to use to connect to the remote BMC.
        auth_type: Ignored.
        ip_address: The IP Address of the BMC.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: (list) Sensor number, id string, and type for each sensor available.

    """
    response = list()
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        result = ipmicmd.get_sensor_descriptions()
        if 'error' in result:
            raise OpenDcreException("Error retrieving sensors from IPMI BMC {} : {}".format(
                    ip_address, result['error']))
        # NB (ABC): The below method is not pleasant, but is the only way to get at the sensor numbers
        #  names and types in a single place without modifying pyghmi.  Later implementation may want to push this
        #  into Command.
        for sensor in ipmicmd._sdr.get_sensor_numbers():
            response.append(
                {
                    'sensor_number': sensor,
                    'id_string': ipmicmd._sdr.sensors[sensor].name,
                    'sensor_type': ipmicmd._sdr.sensors[sensor].sensor_type
                }
            )

        return response


def read_sensor(username=None, password=None, auth_type=None, ip_address=None, ipmi20_enabled=True,
                ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None, sensor_name=None):
    """ Get a converted sensor reading back from the remote system for a given sensor_name.

    Args:
        username: Username to connect to BMC with.
        password: Password to connect to BMC with.
        auth_type: Ignored.
        ip_address: BMC IP Address.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.
        sensor_name: (string) The id_string of the sensor to read. (NB ABC: this is a vestige of pyghmi,
                                                                    it would be better to read by sensor number)

    Returns: (dict) The converted sensor reading for the given sensor_name.  Will raise an IpmiException if the
        sensor is not available (e.g. the power is off).

    """
    if sensor_name is not None:
        result = dict()
        with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
            result['sensor_reading'] = ipmicmd.get_sensor_reading(sensor_name).value
            return result
    raise ValueError("Must specify a sensor name when retrieving sensor reading via IPMI.")


def get_boot(username=None, password=None, auth_type=None, ip_address=None, ipmi20_enabled=True,
             ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Get boot target from remote host.

    Args:
        username: Username to connect to BMC with.
        password: Password to connect to BMC with.
        auth_type: Ignored.
        ip_address: BMC IP Address.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: (dict) Boot target as observed, or IpmiException from pyghmi.

    """
    response = dict()
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        result = ipmicmd.get_bootdev()
        if 'error' in result:
            raise OpenDcreException("Error retrieving boot device from IPMI BMC {} : {}".format(
                    ip_address, result['error']))
        bootdev = result.get('bootdev', 'unknown')
        bootdev = dict(network='pxe', hd='hdd', default='no_override').get(bootdev)
        response['target'] = bootdev
        return response


def set_boot(username=None, password=None, auth_type=None, ip_address=None, target=None, ipmi20_enabled=True,
             ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Set the boot target on remote host.

    Args:
        username: Username to connect to BMC with.
        password: Password to connect to BMC with.
        auth_type: Ignored.
        ip_address: BMC IP Address.
        target: The boot target to set the remote host to.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: (dict) Boot target as observed, or IpmiException from pyghmi.

    """
    response = dict()
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        target = dict(pxe='network', hdd='hd', no_override='default').get(target)
        result = ipmicmd.set_bootdev(bootdev=target)
        if 'error' in result:
            raise OpenDcreException("Error setting boot device from IPMI BMC {} : {}".format(
                    ip_address, result['error']))
        bootdev = result.get('bootdev', 'unknown')
        bootdev = dict(network='pxe', hd='hdd', default='no_override').get(bootdev)
        response['target'] = bootdev
        return response


def get_inventory(username=None, password=None, auth_type=None, ip_address=None, ipmi20_enabled=True,
                  ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Get inventory information from the FRU of the remote system.

    Args:
        username: The username to connect to BMC with.
        password: The password to connect to BMC with.
        auth_type: Ignored.
        ip_address: The IP Address of the BMC.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: (dict) Inventory information from the remote system.

    """
    response = dict()
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        result = ipmicmd.get_inventory_of_component('System')
        if 'error' in result:
            raise OpenDcreException("Error retrieving System inventory from IPMI BMC {} : {}".format(
                    ip_address, result['error']))
        response['chassis_info'] = dict()
        response['chassis_info']['chassis_type'] = result.get('Chassis type', '')
        response['chassis_info']['part_number'] = result.get('Chassis part number', '')
        response['chassis_info']['serial_number'] = result.get('Chassis serial number', '')
        response['board_info'] = dict()
        response['board_info']['manufacturer'] = result.get('Board manufacturer', '')
        response['board_info']['part_number'] = result.get('Board part number', '')
        response['board_info']['product_name'] = result.get('Board product name', '')
        response['board_info']['serial_number'] = result.get('Board serial number', '')
        response['product_info'] = dict()
        response['product_info']['asset_tag'] = result.get('Asset Number', '')
        response['product_info']['part_number'] = result.get('Model', '')
        response['product_info']['manufacturer'] = result.get('Manufacturer', '')
        response['product_info']['product_name'] = result.get('Product name', '')
        response['product_info']['serial_number'] = result.get('Serial Number', '')
        response['product_info']['version'] = result.get('Hardware Version', '')
        return response


def get_identify(username=None, password=None, auth_type=None, ip_address=None, ipmi20_enabled=True,
                 ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Retrieve remote system LED status.

    Args:
        username: Username to connect to BMC.
        password: Password to connect to BMC.
        auth_type: Ignored.
        ip_address: BMC IP Address.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: (dict) LED Status as reported by remote system.

    """
    response = dict()
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        result = ipmicmd.raw_command(netfn=0, command=1, data=[])
        if 'error' in result:
            raise OpenDcreException("Error executing chassis status command on {} : {}".format(ip_address,
                                                                                                result['error']))
        if result['command'] != 1 or result['netfn'] != 1 or result['code'] != 0:
            raise OpenDcreException("Error receiving chassis status response on {} : rc {}".format(
                    ip_address, hex(result['code]'])))
        try:
            if (result['data'][2] >> 5) & 0x01 or (result['data'][2] >> 4) & 0x01:
                response['led_state'] = 1
            else:
                response['led_state'] = 0
            return response
        except (ValueError, Exception), ex:
            raise OpenDcreException("Error retrieving chassis status response data on {} : {}".format(ip_address,
                                                                                                       ex.message))


def set_identify(username=None, password=None, auth_type=None, ip_address=None, led_state=None, ipmi20_enabled=True,
                 ipmi20_auth=None, ipmi20_integrity=None, ipmi20_encryption=None):
    """ Turn the remote system LED on or off.

    Args:
        username: Username to connect to BMC with.
        password: Password to connect to BMC with.
        auth_type: Ignored.
        ip_address: BMC IP Address.
        led_state: (int) 1 == Force on, 0 == Force off.
        ipmi20_enabled: Ignored.
        ipmi20_auth: Ignored.
        ipmi20_integrity: Ignored.
        ipmi20_encryption: Ignored.

    Returns: LED State as set.

    """
    response = dict()
    # Force on if True, Force off if False (indefinite duration)
    state = led_state == 1
    with _IpmiCommand(ip_address=ip_address, username=username, password=password) as ipmicmd:
        ipmicmd.set_identify(on=state)
        response['led_state'] = led_state
        return response
