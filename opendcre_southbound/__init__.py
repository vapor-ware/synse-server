#!/usr/bin/python
"""
   OpenDCRE Southbound API Endpoint
   Author:  andrew
   Date:    4/8/2015
   Update:  6/11/2015 - Support power control commands/responses. Minor bug
                        fixes and sensor/device renaming. (ABC)
            6/19/2015 - Add locking to prevent multiple simultaneous requests
                        from stomping all over the bus.
            7/20/2015 - add node information
            7/28/2015 - convert to python package
            11/6/2015 - add IPMI module support and configuration (v1.1.0)

        \\//
         \/apor IO

    Copyright (C) 2015  Vapor IO

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
import sys
import logging
import json

from flask import Flask
from flask import jsonify
from flask import abort
from lockfile import LockFile  # for sync on the serial bus

from version import __version__  # full opendcre version
from version import __api_version__  # major.minor API version

import devicebus
import vapor_ipmi

PREFIX = "/opendcre/"  # URL prefix for REST access
SERIAL_DEFAULT = "/dev/ttyAMA0"  # default serial device to use for bus
DEBUG = False  # set to False to disable extra logging
LOCKFILE = "/tmp/OpenDCRE.lock"  # to prevent chaos on the serial bus

IPMIFILE = "bmc_config.json"  # BMC settings for IPMI module
IPMI_BOARD_ID = 0x40000000    # set bit 6 of upper byte of board_id to 1=IPMI

app = Flask(__name__)
logger = logging.getLogger()


def __count(start=0x00, step=0x01):
    """ Generator whose next() method returns consecutive values until it reaches
    0xff, then wraps back to 0x00.

    Args:
        start (int): the value at which to start the count
        step (int): the amount to increment the count

    Returns:
        An int representing the next count value.
    """
    n = start
    while True:
        yield n
        n += step
        n %= 0xff

# define a module-level counter, incremented for DeviceBusPacket sequences
_count = __count(start=0x01, step=0x01)


def board_id_to_hex_string(hex_value):
    """ Convenience method to convert a hexadecimal board_id value into its hex
    string representation, without the '0x' prefix, and with left-padding added
    if needed (for a 4 byte width).

    Args:
        hex_value (int): hexadecimal board id value.

    Returns:
        A string representation of the board id.
    """
    return '{0:08x}'.format(hex_value)


def device_id_to_hex_string(hex_value):
    """ Convenience method to convert a hexadecimal device_id value into its hex
    string representation, without the '0x' prefix, and with left- padding added
    if needed (for a 2 byte width).

    Args:
        hex_value (int): hexadecimal device id value.

    Returns:
        A string representation of the device id.
    """
    return '{0:04x}'.format(hex_value)


def is_ipmi_board(board_id):
    """ Convenience method to determine if a board_num is an IPMI board, in
    which case, different processing is to occur.

    Args:
        board_id (int): hexadecimal board id value.

    Returns:
        True if the board is an IPMI board, False otherwise.
    """
    if board_id == IPMI_BOARD_ID:
        return True
    return False


def is_ipmi_device(device_id):
    """ Convenience method to determine if a device_id is valid BMC or not.

    Args:
        device_id (int): hexadecimal device id value.

    Returns:
        True if the device_id maps to a BMC, False otherwise.
    """
    for bmc in app.config['bmcs']['bmcs']:
        if bmc['bmc_device_id'] == device_id:
            return True
    return False


def ipmi_get_bmc_info(board_id, device_id):
    """ Convenience method to get BMC information for a given board and device
    number.

    Args:
        board_id (int): hexadecimal board id value.
        device_id (int): hexadecimal device id value.

    Returns:
        None, if the BMC does not exist, otherwise the BMC record is returned.
    """
    if is_ipmi_board(board_id) and is_ipmi_device(device_id):
        for bmc in app.config['bmcs']['bmcs']:
            if bmc['bmc_device_id'] == device_id:
                return bmc
    return None


def ipmi_get_auth_type(auth_string):
    """ Converts the 'auth_type' field string value to the numeric value used
    by IPMI and vapor_ipmi.

    Args:
        auth_string (str): string value of the auth type.

    Returns:
        The numeric value used by IMPI for the given auth string. If auth_type
        is "NONE", or unable to be determined, AUTH_NONE is returned.
    """
    if auth_string == 'MD5':
        return vapor_ipmi.AUTH_MD5
    elif auth_string == 'MD2':
        return vapor_ipmi.AUTH_MD2
    elif auth_string == 'PASSWORD':
        return vapor_ipmi.AUTH_PASSWORD
    else:
        return vapor_ipmi.AUTH_NONE


def ipmi_scan():
    """ Return a "board" result based on the BMC configuration loaded at app
    initialization. If no BMCs are configured, an empty set of devices is
    returned, otherwise a device entry is returned for each BMC configured.

    Returns:
        A 'board' result based on the BMC configuration.
    """
    response_dict = {
        'board_id': board_id_to_hex_string(IPMI_BOARD_ID),
        'devices': []
    }

    for bmc in app.config['bmcs']['bmcs']:
        response_dict['devices'].append(
            {
                'device_id': device_id_to_hex_string(bmc['bmc_device_id']),
                'device_type': 'power'
            }
        )

    return response_dict


def opendcre_scan(bus):
    """ Query all boards and provide the active devices on each board.
    """
    response_dict = {'boards': []}

    try:
        dr = devicebus.DumpResponse(serial_reader=bus)
    except devicebus.BusTimeoutException:
        abort(500)
    else:
        response_dict['boards'].append(
            {
                'board_id': board_id_to_hex_string(dr.board_id),
                'devices': [
                    {
                        'device_id': device_id_to_hex_string(dr.device_id),
                        'device_type': devicebus.get_device_type_name(dr.data[0])
                    }
                ]
            }
        )
        logger.debug(" * FLASK (scan) <<: " + str([hex(x) for x in dr.serialize()]))

    while True:
        try:
            dr = devicebus.DumpResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            break
        else:
            board_exists = False

            for board in response_dict['boards']:
                if int(board['board_id'], 16) == dr.board_id:
                    board_exists = True
                    board['devices'].append(
                        {
                            'device_id': device_id_to_hex_string(dr.device_id),
                            'device_type': devicebus.get_device_type_name(dr.data[0])
                        }
                    )
                    break

            if not board_exists:
                response_dict['boards'].append(
                    {
                        'board_id': board_id_to_hex_string(dr.board_id),
                        'devices': [{
                            'device_id': device_id_to_hex_string(dr.device_id),
                            'device_type': devicebus.get_device_type_name(dr.data[0])
                        }]
                    }
                )
            logger.debug(" * FLASK (scan) <<: " + str([hex(x) for x in dr.serialize()]))

    return response_dict


@app.route(PREFIX + __api_version__ + "/test", methods=['GET', 'POST'])
def test_routine():
    """ Test routine to verify the endpoint is running and ok, without
        relying on the serial bus layer.
    """
    return jsonify({"status": "ok"})


@app.route(PREFIX + __api_version__ + "/version/<string:boardNum>", methods=['GET'])
def get_board_version(boardNum):
    """ Get board version given the specified board number.

    Args:
        boardNum (str): the board number to get version for.

    Returns:
        The version of the hardware and firmware for the given board.

    Raises:
        Returns a 500 error if the scan command fails.
    """
    try:
        boardNum = int(boardNum, 16)
    except ValueError:
        abort(500)

    with LockFile(LOCKFILE):
        # first check if IPMI
        if is_ipmi_board(boardNum):
            return jsonify({'firmware_version': 'OpenDCRE IPMI Bridge ' + __version__,
                            'opendcre_version': __version__,
                            'api_version': __api_version__})

        # otherwise, hit the bus
        bus = devicebus.initialize(app.config["SERIAL"])
        vc = devicebus.VersionCommand(board_id=boardNum, sequence=next(_count))
        bus.write(vc.serialize())

        logger.debug(" * FLASK (version) >>: " + str([hex(x) for x in vc.serialize()]))

        try:
            vr = devicebus.VersionResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK (version) <<: " + str([hex(x) for x in vr.serialize()]))

        return jsonify({"firmware_version": vr.versionString,
                        "opendcre_version": __version__,
                        "api_version": __api_version__})


@app.route(PREFIX + __api_version__ + "/scan", methods=['GET'])
def scan_all():
    """ Query for all boards, and provide the active devices on each board.

    Returns:
        Active devices, numbers and types from the given board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        dc = devicebus.DumpCommand(board_id=0xff000000, sequence=next(_count))
        bus.write(dc.serialize())

        response_dict = opendcre_scan(bus)

        # now scan IPMI based on configuration
        response_dict['boards'].append(ipmi_scan())
        return jsonify(response_dict)


@app.route(PREFIX + __api_version__ + "/scan/<string:boardNum>", methods=['GET'])
def get_board_devices(boardNum):
    """ Query a specific board, given the board id, and provide the active
    devices on that board.

    Args:
        boardNum (str): the board number to dump. If 0xFF then scan all boards
            on the bus.

    Returns:
        Active devices, numbers and types from the given board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    try:
        boardNum = int(boardNum, 16)
    except ValueError:
        abort(500)

    with LockFile(LOCKFILE):
        if is_ipmi_board(boardNum):
            return jsonify({'boards': [ipmi_scan()]})

        bus = devicebus.initialize(app.config["SERIAL"])
        dc = devicebus.DumpCommand(board_id=boardNum, sequence=next(_count))
        bus.write(dc.serialize())

        response_dict = opendcre_scan(bus)
        return jsonify(response_dict)


@app.route(PREFIX + __api_version__ + "/read/<string:deviceType>/<string:boardNum>/<string:deviceNum>", methods=['GET'])
def read_device(deviceType, boardNum, deviceNum):
    """ Get a device reading for the given board and port and device type.

    We could filter on the upper ID of boardNum in case an unusual board number
    is provided; however, the bus should simply time out in these cases.

    Args:
        deviceType (str): corresponds to the type of device to get a reading for.
            It must match the actual type of device that is present on the bus,
            and is used to interpret the raw device reading.
        boardNum (str): specifies which Pi hat to get the reading from
        deviceNum (str): specifies which device of the Pi hat should be polled
            for device reading.

    Returns:
        Interpreted and raw device reading, based on the specified device type.

    Raises:
        Returns a 500 error if the read command fails.
    """
    try:
        boardNum = int(boardNum, 16)
        deviceNum = int(deviceNum, 16)
    except ValueError:
        abort(500)

    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        src = devicebus.DeviceReadCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                          device_type=devicebus.get_device_type_code(deviceType.lower()))
        bus.write(src.serialize())

        logger.debug(" * FLASK (read) >>: " + str([hex(x) for x in src.serialize()]))

        try:
            srr = devicebus.DeviceReadResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK (read) <<: " + str([hex(x) for x in srr.serialize()]))

        # get raw value as number
        device_raw = ""
        try:
            for x in srr.data:
                device_raw += chr(x)
            device_raw = int(device_raw)
        except:
            abort(500)  # if we cannot convert the reading from bytes to
                        # an integer, we cannot move forward

        # convert raw value and jsonify the device reading
        if deviceType.lower() == "thermistor":
            try:
                converted_value = devicebus.convertThermistor(device_raw)
                return jsonify({"device_raw": device_raw, "temperature_c": converted_value})
            except devicebus.BusDataException:
                # if we saw an invalid value...
                abort(500)
        else:
            # for anything we don't convert, send back raw data
            # for invalid device types / device mismatches, that gets
            # caught when the request is sent over the bus
            return jsonify({"device_raw": device_raw})

@app.route(PREFIX + __api_version__ + "/read/<string:deviceType>/<string:boardNum>/<string:deviceNum>/info", methods=['GET'])
def read_asset_info(deviceType, boardNum, deviceNum):
    """ Get asset information for the given board and port and device type.
    Currently, only 'power' type devices are supported.

    Args:
        deviceType (str): corresponds to the type of device to get a reading for.
            It must match the actual type of device that is present on the bus,
            and is used to interpret the raw device reading.  Only 'power' type
            devices are supported.
        boardNum (str): specifies which board to get the asset info from.
        deviceNum (str): specifies which device should be polled
            for asset info.

    Returns:
        Asset information string, along with board and device number.  For IPMI
        devices, also returns BMC IP.

    Raises:
        Returns a 500 error if the read asset info command fails.
    """
    try:
        boardNum = int(boardNum, 16)
        deviceNum = int(deviceNum, 16)
    except ValueError:
        abort(500)

    if deviceType != 'power':
        abort(500)  # only 'power' devices supported

    with LockFile(LOCKFILE):
        if is_ipmi_board(boardNum):
            if is_ipmi_device(deviceNum):
                try:
                    bmc_info = ipmi_get_bmc_info(boardNum, deviceNum)
                    return jsonify({'board_id': board_id_to_hex_string(boardNum),
                        'device_id': device_id_to_hex_string(deviceNum),
                        'asset_info': bmc_info['asset_info'],
                        'bmc_ip': bmc_info['bmc_ip']})
                except:
                    abort(500)  # unrecoverable error
            else:
                abort(500)  # invalid IPMI device specified

        bus = devicebus.initialize(app.config["SERIAL"])
        src = devicebus.ReadAssetInfoCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                          device_type=devicebus.get_device_type_code(deviceType.lower()))
        bus.write(src.serialize())

        logger.debug(" * FLASK (asset read) >>: " + str([hex(x) for x in src.serialize()]))

        try:
            rair = devicebus.ReadAssetInfoResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK (asset read) <<: " + str([hex(x) for x in rair.serialize()]))

        return jsonify({"board_id": board_id_to_hex_string(boardNum),
            "device_id": device_id_to_hex_string(deviceNum),
            "asset_info": rair.asset_info})

@app.route(PREFIX + __api_version__ + "/write/<string:deviceType>/<string:boardNum>/<string:deviceNum>/info/<string:assetInfo>", methods=['GET'])
def write_asset_info(deviceType, boardNum, deviceNum, assetInfo):
    """ Write asset info for a given device (so long as supported).

    Args:
        deviceType (str): corresponds to the type of device to write to - must
            match the actual type of device that is present on the bus.  Only
            'power' type device supported for non-IPMI boards.
        boardNum (str): specifies which board to write to.
        deviceNum (str): specifies which device to write to.
        assetInfo (str): the asset information to write (127 characters or less)

    Returns:
        Board, device and asset information upon success.

    Raises:
        Returns a 500 error if the write command fails.
    """
    try:
        boardNum = int(boardNum, 16)
        deviceNum = int(deviceNum, 16)
    except ValueError:
        abort(500)

    if deviceType != 'power':
        abort(500)  # only 'power' devices supported

    with LockFile(LOCKFILE):
        if is_ipmi_board(boardNum):
                abort(500)  # write to IPMI asset info not supported

        bus = devicebus.initialize(app.config["SERIAL"])
        src = devicebus.WriteAssetInfoCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                          device_type=devicebus.get_device_type_code(deviceType.lower()),
                                          asset_info=assetInfo[0:127])
        bus.write(src.serialize())

        logger.debug(" * FLASK (asset write) >>: " + str([hex(x) for x in src.serialize()]))

        try:
            wair = devicebus.WriteAssetInfoResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK (asset write) <<: " + str([hex(x) for x in wair.serialize()]))

        return jsonify({"board_id": board_id_to_hex_string(boardNum),
            "device_id": device_id_to_hex_string(deviceNum),
            "asset_info": wair.asset_info})

@app.route(PREFIX + __api_version__ + "/write/<string:deviceType>/<string:boardNum>/<string:deviceNum>", methods=['GET'])
def write_device(deviceType, boardNum, deviceNum):
    """ Write a value to a given device (so long as the device is writeable).

    UNDONE: this method may change considerably as it has not yet been fleshed out.

    Args:
        deviceType (str): corresponds to the type of device to write to - it must
            match the actual type of device that is present on the bus, and may
            be used to interpret the device data.
        boardNum (str): specifies which Pi hat to write to.
        deviceNum (str): specifies which device of the Pi hat should be written
            to.

    Returns:
        Depends on device, but if data returned, success.

    Raises:
        Returns a 500 error if the write command fails.
    """
    # not currently implemented.
    abort(501)


@app.route(PREFIX + __api_version__ + "/power/<string:powerAction>/<string:boardNum>/<string:deviceNum>", methods=['GET'])
def power_control(powerAction, boardNum, deviceNum):
    """ Power on/off/cycle/status for the given board and port and device.

    Args:
        powerAction (str): may be on/off/cycle/status and corresponds to the
            action to take.
        boardNum (str): the id of the board which contains the device that
            accepts power control commands.
        deviceNum (str): the id of the device which accepts power control
            commands.

    Returns:
        Power status of the given device.

    Raises:
        Returns a 500 error if the power command fails.
    """
    try:
        boardNum = int(boardNum, 16)
        deviceNum = int(deviceNum, 16)
    except ValueError:
        abort(500)

    with LockFile(LOCKFILE):
        # first see if we are IPMI, and handle right here if so
        if is_ipmi_board(boardNum) and is_ipmi_device(deviceNum):
            bmc_info = ipmi_get_bmc_info(boardNum, deviceNum)
            if powerAction.lower() == "status" or powerAction.lower() == "on" or powerAction.lower() == "off":
                try:
                    status = vapor_ipmi.power(bmc_info['username'], bmc_info['password'],
                        ipmi_get_auth_type(bmc_info['auth_type']),
                        bmc_info['bmc_ip'], powerAction.lower())

                    # now, convert raw reading into subfields
                    status_converted = {
                        "pmbus_raw": 0,
                        "power_status": status['power_status'],
                        "power_ok": status['power_ok'],
                        "over_current": False,
                        "under_voltage": False,
                        "input_power": 0,
                        "input_voltage": 0,
                        "output_current": 0
                    }

                    return jsonify(status_converted)
                except:
                    abort(500)  # there is nothing we can do to recover here
            elif powerAction.lower() == "cycle":
                try:
                    vapor_ipmi.power(bmc_info['username'], bmc_info['password'],
                        ipmi_get_auth_type(bmc_info['auth_type']),
                        bmc_info['bmc_ip'], "off")
                    status = vapor_ipmi.power(bmc_info['username'], bmc_info['password'],
                        ipmi_get_auth_type(bmc_info['auth_type']),
                        bmc_info['bmc_ip'], "on")

                    # now, convert raw reading into subfields
                    status_converted = {
                        "pmbus_raw": 0,
                        "power_status": status['power_status'],
                        "power_ok": status['power_ok'],
                        "over_current": False,
                        "under_voltage": False,
                        "input_power": 0,
                        "input_voltage": 0,
                        "output_current": 0
                    }

                    return jsonify(status_converted)
                except:
                    abort(500)  # there is nothing we can do here to recover
            else:
                abort(500)  # poweraction is invalid

        # otherwise use the bus for power control
        bus = devicebus.initialize(app.config["SERIAL"])
        if powerAction.lower() == "status":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                                device_type=devicebus.get_device_type_code("power"), power_status=True)
        elif powerAction.lower() == "on":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                                device_type=devicebus.get_device_type_code("power"), power_on=True)
        elif powerAction.lower() == "off":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                                device_type=devicebus.get_device_type_code("power"), power_off=True)
        elif powerAction.lower() == "cycle":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count), device_id=deviceNum,
                                                device_type=devicebus.get_device_type_code("power"), power_cycle=True)
        else:
            abort(500)  # powerAction is invalid

        bus.write(pcc.serialize())

        logger.debug(" * FLASK (power) >>: " + str([hex(x) for x in pcc.serialize()]))

        try:
            pcr = devicebus.PowerControlResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK (power) <<: " + str([hex(x) for x in pcr.serialize()]))

        # get raw value as string
        pmbus_raw = ""
        try:
            for x in pcr.data:
                pmbus_raw += chr(x)
            # here, we should have a comma-separated string that looks like:
            # nstatus,npower,nvoltage,ncurrent
            pmbus_values = pmbus_raw.split(',')
            status_raw = int(pmbus_values[0])
            power_raw = int(pmbus_values[1])
            voltage_raw = int(pmbus_values[2])
            current_raw = int(pmbus_values[3])
        except:
            abort(500)  # if we cannot convert the reading from bytes to
                        # an integer, we cannot move forward

        def convert_power_status(raw):
            if (raw >> 6 & 0x01) == 0x01:
                return "off"
            else:
                return "on"

        def bit_to_bool(raw):
            if raw == 1:
                return True
            else:
                return False

        # now, convert raw reading into subfields
        status_converted = {
            "pmbus_raw": pmbus_raw,
            "power_status": convert_power_status(status_raw),
            "power_ok": not bit_to_bool((status_raw >> 11) & 0x01),
            "over_current": bit_to_bool((status_raw >> 4) & 0x01),
            "under_voltage": bit_to_bool((status_raw) >> 3 & 0x01),
            "input_power": devicebus.convertDirectPmbus(power_raw, "power"),
            "input_voltage": devicebus.convertDirectPmbus(voltage_raw, "voltage"),
            "output_current": devicebus.convertDirectPmbus(current_raw, "current")
        }

        return jsonify(status_converted)


def main(serial_port=SERIAL_DEFAULT, flaskdebug=False):
    """ Main method to run the flask server.

    Args:
        serial_port (str): specify the serial port to use; the default is fine
            for production, but for testing it is necessary to pass in an emulator
            port here.
        flaskdebug (bool): indicates whether debug information is produced by flask.
    """
    app.config["SERIAL"] = serial_port
    #app.debug = True
    if DEBUG is True:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    # read IPMI configuration in at startup
    try:
        ipmifile = open(IPMIFILE, "r")
        app.config['bmcs'] = json.loads(ipmifile.read())
        # validate schema of each BMC:
        for bmc in app.config['bmcs']['bmcs']:
            for key in ['bmc_device_id', 'bmc_ip', 'username', 'password', 'auth_type', 'asset_info']:
                if key not in bmc:
                    raise Exception('Key ' + key + ' missing from BMC configuration.')
    except IOError as e:
        # in this case, there is no config file, or error opening
        # in which case, we log error and cache no bmcs
        logger.debug(" * FLASK (scan) : Error opening BMC Config File : " + str(e))
        app.config['bmcs'] = {'bmcs': []}
    except Exception as e:
        # once again, we do not want to completely kill the endpoint,
        # so we log the exception and cache no bmcs
        logger.debug(" * FLASK (scan) : Error reading BMC Config File : " + str(e))
        app.config['bmcs'] = {'bmcs': []}

    if __name__ == '__main__':
        app.run(host="0.0.0.0")


if len(sys.argv) > 1:
    main(sys.argv[1])
else:
    main()
