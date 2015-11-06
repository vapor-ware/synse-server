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

from flask import Flask
from flask import jsonify
from flask import abort
from lockfile import LockFile  # for sync on the serial bus

from version import __version__  # full opendcre version
from version import __api_version__  # major.minor API version
import devicebus

PREFIX = "/opendcre/"  # URL prefix for REST access
SERIAL_DEFAULT = "/dev/ttyAMA0"  # default serial device to use for bus
DEBUG = False  # set to False to disable extra logging
LOCKFILE = "/tmp/OpenDCRE.lock"  # to prevent chaos on the serial bus

app = Flask(__name__)
logger = logging.getLogger()


def __count(start=0x00, step=0x01):
    """ Generator whose next() method returns consecutive values until it reaches
    0xff, then wraps back to 0x00.
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
    if needed (for a 4 byte width)
    """
    return '{0:08x}'.format(hex_value)


def device_id_to_hex_string(hex_value):
    """ Convenience method to convert a hexadecimal device_id value into its hex
    string representation, without the '0x' prefix, and with left- padding added
    if needed (for a 2 byte width)
    """
    return '{0:04x}'.format(hex_value)


def opendcre_scan(bus):
    """ Query all boards and provide the active devices on each board
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
                'ports': [
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
                    board['ports'].append(
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
                        'ports': [{
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

    Args:  boardNum is the board number to get version for.

    Returns:  The version of the hardware and firmware for the given board.

    Raises:   Returns a 500 error if the scan command fails.

    """
    try:
        boardNum = int(boardNum, 16)
    except ValueError:
        abort(500)

    # TODO: this is a very aggressive locking strategy.  we could release
    #       the lockfile once we've gotten our response back, prior to
    #       returning results.  this could be tidied up.
    with LockFile(LOCKFILE):
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
    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        dc = devicebus.DumpCommand(board_id=0xff000000, sequence=next(_count))
        bus.write(dc.serialize())

        response_dict = opendcre_scan(bus)
        return jsonify(response_dict)


@app.route(PREFIX + __api_version__ + "/scan/<string:boardNum>", methods=['GET'])
def get_board_ports(boardNum):
    """ Query a specific board, given the board id, and provide the
        active devices on that board.

    Args:  boardNum is the board number to dump.  If 0xFF then scan
            all boards on the bus.

    Returns:  Active device ports, numbers and types from the given board(s).

    Raises:   Returns a 500 error if the scan command fails.

    """
    try:
        boardNum = int(boardNum, 16)
    except ValueError:
        abort(500)

    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        dc = devicebus.DumpCommand(board_id=boardNum, sequence=next(_count))
        bus.write(dc.serialize())

        response_dict = opendcre_scan(bus)
        return jsonify(response_dict)


@app.route(PREFIX + __api_version__ + "/read/<string:deviceType>/<string:boardNum>/<string:deviceNum>", methods=['GET'])
def read_device(deviceType, boardNum, deviceNum):
    """ Get a device reading for the given board and port and device type.

    Args:  the deviceType corresponds to the type of device to get a reading
    for - it must match the actual type of device that is present on the bus,
    and is used to interpret the raw device reading.  The boardNum specifies
    which Pi hat to get the reading from, while the portNum specifies which port
    of the Pi hat should be polled for device reading.

    Returns:  Interpreted and raw device reading, based on the specified device
              type.

    Raises:   Returns a 500 error if the scan command fails.

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


@app.route(PREFIX + __api_version__ + "/write/<string:deviceType>/<string:boardNum>/<string:deviceNum>", methods=['GET'])
def write_device(deviceType, boardNum, deviceNum):
    """ Write a value to a given device (so long as the device is writeable).

    Args:  the deviceType corresponds to the type of device to write to
    - it must match the actual type of device that is present on the bus,
    and may be used to interpret the device data.  The boardNum specifies
    which Pi hat to write to, while the portNum specifies which port
    of the Pi hat should be written to.  UNDONE:  this method may change
    considerably as it has not yet been fleshed out.

    Returns:  Depends on device, but if data returned, success.

    Raises:   Returns a 500 error if the write command fails.

    """
    # not currently implemented.  we may need for the demo, but until then,
    # left undone
    abort(501)


@app.route(PREFIX + __api_version__ + "/power/<string:powerAction>/<string:boardNum>/<string:deviceNum>", methods=['GET'])
def power_control(powerAction, boardNum, deviceNum):
    """ Power on/off/cycle/status for the given board and port and device.

    Args:  powerAction may be on/off/cycle/status and corresponds to the action
    to take.  The boardNum and portNum must correspond to a device that accepts
    power control commands.

    Returns:  Power status of the given device.

    Raises:   Returns a 500 error if the power command fails.

    """
    try:
        boardNum = int(boardNum, 16)
        deviceNum = int(deviceNum, 16)
    except ValueError:
        abort(500)

    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        if powerAction.lower() == "status":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count),
                        device_type=devicebus.get_device_type_code("power"), device_id=deviceNum, power_status=True)
        elif powerAction.lower() == "on":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count),
                        device_type=devicebus.get_device_type_code("power"), device_id=deviceNum, power_on=True)
        elif powerAction.lower() == "off":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count),
                        device_type=devicebus.get_device_type_code("power"), device_id=deviceNum, power_off=True)
        elif powerAction.lower() == "cycle":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=next(_count),
                        device_type=devicebus.get_device_type_code("power"), device_id=deviceNum, power_cycle=True)
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

    Args:  serial_port - specify the serial port to use; the default is fine
    for production, but for testing it is necessary to pass in an emulator
    port here.  Tcp_port is the TCP port that flask should listen on.
    Flaskdebug indicates whether debug information is produced by flask.
    """
    app.config["SERIAL"] = serial_port
    app.debug = True
    if DEBUG is True:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
    if __name__ == '__main__':
        app.run(host="0.0.0.0")


if len(sys.argv) > 1:
    main(sys.argv[1])
else:
    main()
